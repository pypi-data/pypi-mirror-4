#!/usr/bin/env python
"""
Module SigChldMixin
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SigChldMixin class``, which allows
parent processes to respond to SIGCHLD by reaping any
child processes that have completed. The code is
general enough that it should be useful for any process
that wants to fork children and reap them properly. See
the method docstrings for notes on the particular strategy
chosen in this class for handling SIGCHLD. Note that this
functionality is only useful on platforms (e.g., *not*
Windows) that have SIGCHLD; however, the other methods of
the class, which actually do the tracking and reaping of
children, can be used on all platforms provided that some
other mechanism is used to trigger them.
"""

import os
import signal


class SigChldMixin(object):
    """Mixin class for parent processes to properly reap dead children.
    
    This class implements logic to reap zombie children when they
    exit. The logic here is general; for a mixin that is specifically
    designed for use with PLIB servers, see ``SigChldServerMixin``.
    The key requirement is that the ``track_child`` method must be
    called on each child instance when it is constructed (the
    ``SigChldServerMixin`` class does this in the ``_new_child``
    method, right before the new child object is returned). The
    only assumption made is that each ``child`` is an instance of
    the ``ProcessWrapper`` class in ``plib.stdlib.comm._processwrapper``,
    since that API is used to interact with children.
    """
    
    active_children = None
    reaping = False
    
    def setup_child_sig_handler(self):
        """Set up the SIGCHLD handler.
        """
        if hasattr(signal, 'SIGCHLD'):
            signal.signal(signal.SIGCHLD, self.child_sig_handler)
    
    def child_sig_handler(self, sig, frame=None):
        # Reap children
        self.reap_children()
        # Ensure BSD semantics
        signal.signal(signal.SIGCHLD, self.child_sig_handler)
    
    def track_child(self, child):
        """Start tracking a new child process.
        """
        
        if self.active_children is None:
            self.active_children = []
        self.active_children.append(child)
    
    def _wait_children(self):
        # Internal routine to wait for children that have exited.
        if self.active_children is None:
            return
        
        # XXX: This loop runs more system calls than it ought
        # to. There should be a way to put the active_children into a
        # process group and then use os.waitpid(-pgid) to wait for any
        # of that set, but I couldn't find a way to allocate pgids
        # that couldn't collide.
        removes = []
        for child in self.active_children:
            if child.check():
                removes.append(child)
        for child in removes:
            self.active_children.remove(child)
    
    def reap_children(self):
        """Reap children if any are waiting.
        
        If we received SIGCHLD, it will break us out of any pending system
        call; this method is intended to be called before re-starting the
        system call to ensure that there are no zombies remaining.
        
        You may ask: why not just set the SA_RESTART flag when we call
        sigaction to set up our SIGCHLD handler? Then we could just reap
        children inside the handler without affecting the logic of our
        main program loop. There are several reasons why we don't do that
        in this library. First, the select system call is not supposed
        to be restartable in this way, and many of the use cases for
        this class will likely involve select (this includes adding
        SIGCHLD handling to the forking socket server in the PLIB I/O
        sub-package, since that server's main loop uses select in order
        to enable the self-pipe trick for termination signals). Second,
        even for system calls which are restartable (e.g., the accept
        call, which a forking server that didn't use the self-pipe trick
        could use as its main "waiting" call), the SA_RESTART flag is
        not guaranteed to produce the desired semantics on all platforms.
        Third, the timing of Python signal handlers when a signal arrives
        during a system call is not the same as the timing of a signal
        handler in a C program would be. A C signal handler runs at
        interrupt time--i.e., as soon as the signal is received. But a
        Python signal handler does not; at the C level, the Python
        interpreter just sets a flag inside its signal handler and
        returns. The Python handler, if one is installed, does not run
        until the interpreter can pause between bytecodes to switch
        context and run it--which it can't do while a system call is in
        progress, because the interpreter doesn't have control, the
        kernel does. This means that, as far as the kernel-level system
        call is concerned, the "signal handler" is actually finished when
        the C code inside the interpreter sets the flag--which means that
        even if the SA_RESTART flag were set, it would not cause the
        *Python* signal handler to run when we want it to run, which is
        soon after the signal arrives. Instead, the Python handler would
        not run until some *other* event caused the pending system call,
        which was restarted by the kernel because SA_RESTART was set, to
        return! So for Python signal handlers, our only choice is to let
        the signal interrupt the system call, which will then return, at
        the C level, with an EINTR error; the interpreter then checks
        the signal flag, sees that a signal was received, and runs our
        Python signal handler when we want it run, right after the signal
        arrived. It's true that whatever Python code originally made the
        system call now has to know to restart the call if an EINTR error
        occurs, but that code has to know that anyway, because it has to
        know to check the flag that our Python signal handler set, so it
        can reap children.
        """
        
        if not self.reaping:
            self.reaping = True
            self._wait_children()
            self.reaping = False
    
    def close_children(self):
        """Close all active children unconditionally.
        
        Intended to be called when the parent is shutting down.
        """
        
        # This keeps us from being interrupted by SIGCHLD while we're
        # closing down the children by hand (on some platforms, e.g.
        # OS X, the parent can be interrupted by SIGCHLD when a child
        # exits even if it's already inside a waitpid system call on
        # the *same* child)
        if hasattr(signal, 'SIGCHLD'):
            signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        if self.active_children is not None:
            for child in self.active_children:
                child.end()
            del self.active_children

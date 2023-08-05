#!/usr/bin/env python
"""
Module SigChldServerMixin
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SigChldServerMixin`` class, which
specializes ``SigChldMixin`` for servers conforming to the
PLIB I/O server API. The original use case for this class
is as a mixin for the forking ``SocketServer`` class in
``plib.io.blocking``.
"""

import signal

from .SigChldMixin import SigChldMixin


class SigChldServerMixin(SigChldMixin):
    """Mixin class for PLIB servers to properly reap dead children.
    """
    
    ignore_sigchld = False  # Overrides default for ForkingServer
    
    def server_start(self):
        # Override to set up the signal handler
        super(SigChldServerMixin, self).server_start()
        if hasattr(signal, 'SIGCHLD'):
            pipe = getattr(self, 'pipe', None)
            if (pipe is not None):
                # If we are using the self-pipe trick (if so, the
                # SelfPipeServerMixin class should have set up the
                # pipe in the super call above), we use its
                # mechanism to track signals; note that we ask for
                # the signal handler to be reset each time to
                # ensure BSD semantics
                self.pipe.track_signal(signal.SIGCHLD, reset=True)
            else:
                self.setup_child_sig_handler()
    
    def _new_child(self, handler, conn, addr):
        child = super(SigChldServerMixin, self)._new_child(
            handler, conn, addr)
        self.track_child(child)
        return child
    
    def start_child(self, handler, conn, addr):
        """Start a new child process and keep track of it.
        
        Note that we call ``reap_children`` here only as a last
        resort safety measure, in case any are missed by the reaping
        in response to the SIGCHLD handler (or in case we're on a
        platform that doesn't have SIGCHLD--see the module docstring
        for ``SigChldMixin``).
        """
        
        self.reap_children()
        super(SigChldServerMixin, self).start_child(handler, conn, addr)
    
    def signal_callback(self, sig):
        # This is called if the self-pipe trick is being used, once
        # for each signal received; we only handle SIGCHLD here and
        # pass other signals on
        if sig == signal.SIGCHLD:
            self.reap_children()
        else:
            super(SigChldServerMixin, self).signal_callback(sig)
    
    def server_close(self):
        """Terminate all children when the server closes.
        """
        self.close_children()
        super(SigChldServerMixin, self).server_close()

#!/usr/bin/env python
"""
Module SelfPipe
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SelfPipe`` class, which implements
the self-pipe trick in a general way that can be used by any
application wanting to multiplex socket I/O with signals.
"""

from itertools import izip

from plib.stdlib import sigtools


class SelfPipe(object):
    """Self-pipe manager.
    
    Wraps the low-level API provided by the ``sigtools``
    module, which uses the ``set_wakeup_fd`` mechanism in
    the Python ``signal`` module.
    """
    
    def __init__(self, callback):
        self.pipe_fd = sigtools.selfpipe_fd()
        self.callback = callback
        self.old_handlers = {}
    
    def fileno(self):
        return self.pipe_fd
    
    def track_signal(self, sig, reset=False):
        self.old_handlers[sig] = sigtools.track_signal(sig, reset)
    
    def track_signals(self, *sigs):
        for sig, handler in izip(sigs, sigtools.track_signals(*sigs)):
            self.old_handlers[sig] = handler
    
    def send_signal(self, sig):
        sigtools.send_signal(sig)
    
    def receive_signals(self):
        for sig in sigtools.signals_received():
            self.callback(sig)

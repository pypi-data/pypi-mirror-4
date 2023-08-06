#!/usr/bin/env python
"""
Module SigIntServerMixin
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SigIntServerMixin`` class. This
class customizes ``SigIntMixin`` for use with PLIB servers.
It is useful when simple termination signal functionality is
desired without all the extra frills of ``PServerBase``.
"""

from plib.stdlib.classes import SigIntMixin


class SigIntServerMixin(SigIntMixin):
    """Mixin class for PLIB servers to do controlled shutdown on Ctrl-C.
    
    Overrides ``server_start`` to set up the signal handler.
    
    The default of exiting on Ctrl-C (SIGINT) can be changed by
    overriding the ``term_sigs`` class field; it should contain
    a list of signals to be treated as "terminate" signals. See
    the ``PServerBase`` class for an example.
    """
    
    terminate_flag = False
    
    def server_start(self):
        # Override to set up the signal handler
        super(SigIntServerMixin, self).server_start()
        pipe = getattr(self, 'pipe', None)
        if (pipe is not None):
            # If we are using the self-pipe trick (if so, the
            # SelfPipeServerMixin class should have set up the
            # pipe in the super call above), we use its
            # mechanism to track signals; when the self-pipe
            # is read from, it will call self.signal_callback
            for sig in self.term_sigs:
                self.pipe.track_signal(sig)
        else:
            # This uses the mechanism inherited from SigIntMixin,
            # which calls self.terminate_process
            self.setup_term_sig_handler()
    
    def signal_callback(self, sig):
        # This is called if the self-pipe trick is being used, once
        # for each signal received; we only handle our signals here
        # and pass the rest on
        if sig in self.term_sigs:
            self.terminate_process()
        else:
            super(SigIntServerMixin, self).signal_callback(sig)
    
    def terminate_process(self):
        """Tell the server to break out of its ``serve_forever`` loop.
        """
        self.terminate_flag = True
    
    def keep_running(self):
        return (super(SigIntServerMixin, self).keep_running()
            and not self.terminate_flag)

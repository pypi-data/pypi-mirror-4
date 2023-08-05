#!/usr/bin/env python
"""
Module ClientMixin
Sub-Package IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O ClientMixin class.
"""

from plib.io.comm import ClientCommunicator


class ClientMixin(ClientCommunicator):
    """Mixin class for blocking client-side I/O channel.
    """
    
    def run_loop(self, callback=None):
        try:
            while 1:
                while self.writable():
                    self.handle_write()
                while self.readable():
                    self.handle_read()
                if callback is not None:
                    c = callback()
                else:
                    c = None
                if self.done or (c is False):
                    break
        
        except:
            # We can only call close here on an exception, not always,
            # because if keep_alive is True we will break out of the
            # above loop after each round-trip data exchange, but we
            # will *not* want to close the channel
            self.close()
            raise
    
    def run_wait_loop(self, obj, attrname):
        try:
            while not getattr(obj, attrname):
                while self.readable():
                    self.handle_read()
        except:
            self.close()
            raise

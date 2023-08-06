#!/usr/bin/env python
"""
Module ServerMixin
Sub-Package IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O ServerMixin class.
"""

from plib.io.comm import ServerCommunicator


class ServerMixin(ServerCommunicator):
    """Mixin class for blocking server-side I/O channel.
    """
    
    def run_loop(self, callback=None):
        # This allows for an initial "greeting" message
        while self.writable():
            self.handle_write()
        while 1:
            while self.readable():
                self.handle_read()
            while self.writable():
                self.handle_write()
            if callback is not None:
                c = callback()
            else:
                c = None
            if self.done or (c is False):
                break

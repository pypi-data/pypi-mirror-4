#!/usr/bin/env python
"""
Module SocketClientMixin
Sub-Package IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O SocketClientMixin class.
"""

from plib.io.socket import BaseClient
from plib.io.blocking import ClientMixin


class SocketClientMixin(BaseClient, ClientMixin):
    """Mixin class for client-side blocking socket I/O.
    """
    
    def setup_client(self, addr=None):
        old_addr = self.addr
        super(SocketClientMixin, self).setup_client(addr)
        
        # If we just connected above, fire the connect event
        # (we test because it's possible for this method to
        # be called multiple times for one connection)
        if (not old_addr) and (self.addr == addr):
            self.handle_connect()

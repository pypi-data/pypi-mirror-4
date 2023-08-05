#!/usr/bin/env python
"""
Module BaseClient
Sub-Package IO.SOCKET of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the socket BaseClient class.
"""

from plib.io.socket import ConnectMixin


class BaseClient(ConnectMixin):
    """Base class for socket clients.
    """
    
    def setup_client(self, addr):
        """Connect to server at addr.
        
        Note that we don't try to connect if we're already
        connected; this means that if we're connected but
        the ``addr`` parameter does not match the address
        we're currently connected to, the new ``addr`` is
        silently ignored and the original connection remains.
        """
        if not self.addr:
            self.do_connect(addr)

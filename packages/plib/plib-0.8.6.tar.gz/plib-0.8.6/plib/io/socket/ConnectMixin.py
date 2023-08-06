#!/usr/bin/env python
"""
Module ConnectMixin
Sub-Package IO.SOCKET of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the socket ConnectMixin class.
"""

import socket


class ConnectMixin(object):
    """Mixin class to add socket connect functionality.
    """
    
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    
    def do_connect(self, addr):
        """Convenience method to create socket and connect to addr.
        """
        self.create_socket(self.address_family, self.socket_type)
        self.connect(addr)

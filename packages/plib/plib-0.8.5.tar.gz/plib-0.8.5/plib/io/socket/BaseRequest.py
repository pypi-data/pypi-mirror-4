#!/usr/bin/env python
"""
Module BaseRequest
Sub-Package IO.SOCKET of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the socket I/O BaseRequest class.
"""


class BaseRequest(object):
    """Base socket I/O class set up to serve as a request handler.
    """
    
    def __init__(self, request, client_addr, server):
        self.request = request
        self.client_address = client_addr
        self.server = server

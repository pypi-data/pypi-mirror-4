#!/usr/bin/env python
"""
Module RequestBase
Sub-Package IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O RequestBase class.
"""

import sys

from plib.io.socket import BaseRequest
from plib.io.blocking import SocketBase


class RequestBase(BaseRequest, SocketBase):
    """Base class for blocking socket request handler.
    """
    
    def __init__(self, request, client_addr, server):
        BaseRequest.__init__(self, request, client_addr, server)
        SocketBase.__init__(self, request)
        
        # If we're being called at all, we must be connected
        self.handle_connect()
        
        # A blocking request handler runs its own comm loop
        try:
            self.run_loop()
        finally:
            self.close()
            sys.exc_traceback = None # Help garbage collection

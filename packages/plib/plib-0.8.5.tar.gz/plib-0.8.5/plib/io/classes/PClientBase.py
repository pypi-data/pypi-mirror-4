#!/usr/bin/env python
"""
Module PClientBase
Sub-Package IO.CLASSES of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PClientBase class. This is a
mixin for socket I/O clients that provides a number of
conveniences to streamline the process of getting data
from servers. It can be mixed in with both async and
blocking I/O clients.
"""

import sys
import socket


class PClientBase(object):
    """Base client class with conveniences.
    
    Connects with a server, writes data, and stores the
    result. Implemented so that several different usage
    methods will work:
    
    - A single loop can be run by just instantiating the
      class with all the necessary information::
    
        # import the appropriate SocketClient (async/blocking)
        
        class MyClient(PClientBase, SocketClient):
            pass
        
        result = MyClient(data, server_addr).result()
    
    - Repeated single loops can be run by subclassing to
      fill in the constant information::
    
        class MyClient(PClientBase, SocketClient):
            server_addr = my_server_addr
        
        client = MyClient()
        result1 = client(data1)
        result2 = client(data2)
    
    - Multiple loops can be run with a single call
      by overriding the ``process_data`` method to queue
      more data.
    
    The ``client_communicate`` method can also be called,
    as normal, but it is not necessary.
    """
    
    server_addr = ("localhost", 9999)
    raise_error = True
    
    def __init__(self, data=None, addr=None, callback=None):
        super(PClientBase, self).__init__()
        if (addr is None) and self.server_addr:
            addr = self.server_addr
        if data:
            self.client_communicate(data, addr, callback)
        elif addr:
            self.setup_client(addr)
    
    def __call__(self, data, addr=None, callback=None):
        self.client_communicate(data, addr, callback)
        return self._reply
    
    def client_communicate(self, data, client_id=None, callback=None):
        if client_id is None:
            client_id = self.server_addr
        self._reply = None
        try:
            super(PClientBase, self).client_communicate(
                data, client_id, callback)
        except socket.error:
            sys.stderr.write(
                "failed to connect to server at %s, port %s.\n" %
                client_id)
            if self.raise_error:
                raise
    
    def process_data(self):
        self._reply = self.read_data
    
    def result(self):
        return self._reply

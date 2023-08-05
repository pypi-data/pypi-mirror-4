#!/usr/bin/env python
"""
Module BaseServer
Sub-Package IO.SOCKET of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the socket BaseServer class.
"""

import socket


class BaseServer(object):
    """Base socket server class
    
    Sets up socket to listen on specified address.
    """
    
    address_family = socket.AF_INET
    allow_reuse_address = False
    request_queue_size = 5
    socket_type = socket.SOCK_STREAM
    
    def __init__(self, server_addr, handler_class):
        self.handler = handler_class
        
        self.server_start()  # for initialization before socket is created
        
        self.create_socket(self.address_family, self.socket_type)
        if self.allow_reuse_address:
            self.set_reuse_addr()
        self.bind(server_addr)
        self.listen(self.request_queue_size)
    
    def serve_forever(self, callback=None):
        """Handle requests until doomsday.
        
        Runs the accept/request handling loop, and ensures that
        the server is closed on loop exit.
        
        A ``callback`` parameter is provided for cases where the
        ``keep_running`` hook is not suitable. The callback must be
        a zero-argument callable; it should return ``False`` (not
        just a false value, but the specific object) if the loop
        should exit. Requiring the specific object ``False`` is so
        that callbacks can, if desired, be procedures that do not
        return a value (meaning the return defaults to ``None``).
        """
        
        try:
            self.server_loop(callback)
        finally:
            self.close()
    
    # Methods which may be overridden by derived classes
    
    def server_start(self):
        """Placeholder for derived classes.
        """
        pass
    
    def keep_running(self):
        """Check whether server should break out of the serve_forever loop.
        
        The ``server_loop`` method should check this method every time
        it begins a new iteration of the loop. This method is factored
        out to provide a convenient hook within the loop. Note that if
        this method is not overridden, the loop should never exit unless
        an exception occurs.
        """
        return True
    
    def server_close(self):
        """Placeholder for derived classes.
        """
        pass
    
    # Methods which must be implemented by derived classes
    
    def server_loop(self, callback=None):
        """Run the accept/request handling loop.
        
        This method must be implemented in derived classes to run
        the standard socket server loop: wait for an incoming
        request, accept it, and hand it off to a request handler.
        It must also support the semantics described above for
        triggering a loop exit (the ``keep_running`` method returning
        a false value, or the ``callback`` callable, if present,
        returning the specific object ``False``).
        """
        raise NotImplementedError

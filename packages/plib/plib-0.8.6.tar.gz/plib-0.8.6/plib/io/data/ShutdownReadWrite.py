#!/usr/bin/env python
"""
Module ShutdownReadWrite
Sub-Package IO.DATA of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ShutdownReadWrite alternate data
handling class.
"""

import socket


class ShutdownReadWrite(object):
    """Data handling class using socket shutdown.
    
    Mixin read/write class that calls ``shutdown`` on its socket
    when it is finished writing, and detects the end of data
    being read by the read end of the socket closing (which
    is signalled by a read of zero bytes). Obviously, this
    method only works for a single round-trip data exchange.
    Also, this method is only designed to work with sockets;
    hence, the ``shutdown`` method assumes that the socket
    instance variable contains a socket.
    
    Note that the ``auto_close`` class field here is set to
    ``False`` (which means that this class must come *before*
    the ``BaseData`` class in the MRO), so that the channel will
    not automatically be closed when a read of zero bytes is
    detected. This is so that the ``shutdown`` method strategy
    described above will work properly (since it requires that
    each endpoint shut itself down separately, instead of the
    entire channel being closed at once).
    """
    
    auto_close = False
    write_started = False
    
    def read_complete(self):
        # The shutdown_received flag is set by BaseData, which
        # must be somewhere earlier in the MRO
        return self.shutdown_received
    
    def handle_write(self):
        self.write_started = True
        super(ShutdownReadWrite, self).handle_write()
    
    def clear_write(self):
        super(ShutdownReadWrite, self).clear_write()
        if self.write_started:
            self.shutdown()
            self.write_started = False
    
    def shutdown(self):
        if self.shutdown_received:
            # Calling shutdown when the other end already has
            # can lead to undefined behavior; safer to just
            # close instead
            self.close()
        else:
            self.socket.shutdown(socket.SHUT_WR)

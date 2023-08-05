#!/usr/bin/env python
"""
Module SocketBase
Sub-Package IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O SocketBase class.
"""

from plib.io.socket import SocketData, SocketIOBase


class SocketBase(SocketData, SocketIOBase):
    """Base blocking socket I/O class with data handling.
    """
    
    def handle_connect(self):
        self.on_connect()
    
    def on_connect(self):
        """Placeholder for derived classes.
        """
        pass
    
    def readable(self):
        """We can always read from a blocking socket.
        """
        return True
    
    def writable(self):
        """We can always write to a blocking socket.
        """
        return True
    
    def close(self):
        if not self.closed:
            self.handle_close()
        super(SocketBase, self).close()
    
    def handle_close(self):
        self.on_close()
    
    def on_close(self):
        """Placeholder for derived classes.
        """
        pass

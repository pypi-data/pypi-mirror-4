#!/usr/bin/env python
"""
Module ServerCommunicator
Sub-Package IO.COMM of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ServerCommunicator class.
"""

from plib.io.base import BaseCommunicator


class ServerCommunicator(BaseCommunicator):
    """Communicator specialized for server-side I/O.
    
    Assumes a "server" data pattern: read data first, then
    write back the response after processing. Override the
    ``process_data`` method to do something with received data.
    Expects a class earlier in the MRO to implement the
    ``start``, ``handle_read``, ``handle_write``, ``read_complete``,
    ``write_complete``, ``clear_read``, and ``clear_write``
    methods (the intent is that this will be ``BaseData``
    or a class derived from it).
    """
    
    keep_alive = True  # servers shouldn't assume they can shut down
    
    def readable(self):
        return not (self.writable() or self.read_complete() or self.done)
    
    def handle_read(self):
        super(ServerCommunicator, self).handle_read()
        if self.read_complete():
            self.process_data()
            self.clear_read()
    
    def writable(self):
        return not (self.write_complete() or self.done)
    
    def handle_write(self):
        super(ServerCommunicator, self).handle_write()
        if self.write_complete():
            self.clear_write()
            self.check_done()

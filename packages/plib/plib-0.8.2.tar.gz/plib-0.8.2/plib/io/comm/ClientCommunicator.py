#!/usr/bin/env python
"""
Module ClientCommunicator
Sub-Package IO.COMM of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ClientCommunicator class.
"""

from plib.io.base import BaseCommunicator


class ClientCommunicator(BaseCommunicator):
    """Communicator specialized for client-side I/O.
    
    Assumes a "client" data pattern: writes ``write_data``,
    then reads back ``read_data``, processes the data, then
    clears data and checks if done. Call ``client_communicate``
    to run the communication loop. Override ``process_data``
    to do something with the received data. Expects a class
    earlier in the MRO to implement the ``start``, ``handle_read``,
    ``handle_write``, ``read_complete``, ``write_complete``,
    ``clear_read``, and ``clear_write`` methods (the intent
    is that this will be ``BaseData`` or a class derived
    from it).
    """
    
    waiting = False
    
    def writable(self):
        return not (self.waiting or self.write_complete() or self.done)
    
    def handle_write(self):
        super(ClientCommunicator, self).handle_write()
        if self.write_complete():
            self.clear_write()
    
    def readable(self):
        return not (self.writable() or self.read_complete() or self.done)
    
    def handle_read(self):
        super(ClientCommunicator, self).handle_read()
        if self.read_complete():
            self.process_data()
            self.clear_read()
            self.check_done()
    
    def query_done(self):
        """Clients should exit the communication loop if no data pending.
        
        If ``keep_alive`` is true, the channel will remain open, but
        no more data will be exchanged until ``client_communicate`` is
        called again.
        """
        
        return (not self.data_pending) or \
            super(ClientCommunicator, self).query_done()
    
    def wait_for(self, obj, attrname):
        """Force reading only until attrname of obj is True.
        
        Main intended use case is to call this method before starting the
        communication loop for cases where an initial "greeting" is
        expected from the server before we can start sending data.
        """
        
        self.waiting = True
        self.run_wait_loop(obj, attrname)
        self.waiting = False
    
    def client_communicate(self, data, client_id=None, callback=None):
        """Push data for writing and run client-side communication loop.
        
        Core method to implement client I/O functionality:
        connects to server, writes data, reads back the reply,
        processes it, then checks to see if it is done.
        
        Note that if the ``query_done`` method returns false
        (it will be called from ``check_done`` on each iteration),
        it should either call the ``start`` method to supply
        more data to be written, or ensure that ``write_complete``
        is ``True``; otherwise the client may block forever
        waiting for data.
        
        Also note that if ``client_id is None``, we assume that
        the client is already connected to the server and don't
        try to connect again.
        """
        
        self.start(data)
        if client_id is not None:
            self.setup_client(client_id)
        self.run_loop(callback)
    
    # Methods which must be implemented by derived classes
    
    def setup_client(self, client_id):
        """Prepare client for communication.
        """
        raise NotImplementedError
    
    def run_wait_loop(self, obj, attrname):
        """Run read-only communication loop until obj.attrname is true.
        
        Will also exit loop if self.query_done() is true.
        """
        raise NotImplementedError

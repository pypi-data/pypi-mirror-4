#!/usr/bin/env python
"""
Module SocketDispatcher -- Asynchronous Socket I/O
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a basic asynchronous socket I/O
dispatcher.
"""

import socket
from errno import EALREADY, EBADF, EINPROGRESS, EWOULDBLOCK, errorcode

from plib.io.socket import SocketIOBase

from _async import AsyncBase

connect_in_progress_values = [EINPROGRESS, EALREADY, EWOULDBLOCK]


class SocketDispatcher(SocketIOBase, AsyncBase):
    """Base "dispatcher" class for async sockets.
    
    This dispatcher class fixes a number of minor issues
    with asyncore.dispatcher. Key changes:
    
    - Correctly handles the case where a non-blocking connect
      attempt fails; asyncore.dispatcher ends up bailing to
      ``handle_error`` on the first read or write attempt to the
      socket, but aside from being ugly, this doesn't work if
      the dispatcher won't return ``True`` for ``readable`` or
      ``writable`` until it knows the connect has succeeded--it
      will just hang forever in the polling loop--but this class
      spots the socket error and raises an exception so the loop
      exits.
    
    - The ``handle_error`` method is changed to close the socket
      and then re-raise whatever exception caused it to be called
      (much more Pythonic) -- this behavior is inherited from
      ``AsyncBase``.
    
    - The ``handle_close`` method is called from ``close``,
      instead of the reverse (having the method that's intended
      to be a placeholder call a method that needs to always be
      called makes no sense, and the naming is more consistent if
      the "handle" method is the placeholder).
    """
    
    connect_pending = False
    
    def __init__(self, sock=None, map=None):
        AsyncBase.__init__(self, map)
        SocketIOBase.__init__(self, sock)
    
    def repr_status(self, status):
        if self.accepting and self.addr:
            status.append('listening')
        elif self.connected:
            status.append('connected')
        if self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
    
    def set_socket(self, sock):
        SocketIOBase.set_socket(self, sock)
        sock.setblocking(0)
        self.set_fileobj(sock, self._map)
    
    def accept(self):
        try:
            return self.socket.accept()
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                return (None, None)
            else:
                raise
    
    def connect_in_progress(self, value):
        return value in connect_in_progress_values
    
    def connect(self, address):
        self.connected = False
        self.connect_pending = False
        err = self.socket.connect_ex(address)
        # FIXME: Add Winsock return values?
        if self.connect_in_progress(err):
            # The connect will be completed asynchronously, so
            # set a flag to signal that we're waiting
            self.connect_pending = True
            self.closed = False
        elif self.connect_confirmed(err):
            self.addr = address
            self.connected = True
            self.closed = False
            self.handle_connect()
        else:
            raise socket.error, (err, errorcode[err])
    
    def check_error(self):
        try:
            err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        except socket.error, why:
            # This catches EBADF, which signals that our socket has closed;
            # we check for that here because there are conditions where we
            # can't be sure we will get notified any other way (e.g., if
            # we are using select instead of poll, since select can't report
            # exceptions to a specific fd
            err = why[0]
        if err:
            self.close()
            if err != EBADF:
                # Re-raise the error so any pending operation aborts
                raise socket.error, (err, errorcode[err])
    
    def check_connect(self):
        if self.connect_pending:
            self.connect_pending = False
            # We're waiting for a connect to be completed
            # asynchronously, so we need to see if it really
            # was completed or if an error occurred
            self.check_error()
            # If we get here, the connect was successful, so
            # fill in the address
            self.addr = self.socket.getpeername()
        
        # Always set this flag since we only get called if
        # it wasn't already set
        self.connected = True
    
    def readable(self):
        """Check for socket error before allowing read.
        """
        self.check_error()
        return not self.closed
    
    def writable(self):
        """Check for socket error before allowing write.
        """
        self.check_error()
        return not self.closed
    
    def keep_open_on_exc(self, why):
        # This will keep the socket open if send/recv raises EWOULDBLOCK
        # (which will happen if the fd goes unready between the return
        # of the select/poll call and the send/recv)
        return why[0] == EWOULDBLOCK
    
    def handle_read_event(self):
        if self.accepting:
            # Handle the accept--this should be the only read
            # we ever see, since we hand off the actual connection
            # to another socket
            self.handle_accept()
        else:
            # Getting a read implies that we are connected, so
            # we first check to see if we were waiting for a connect
            # to be completed asynchronously and verify it if so
            if not self.connected:
                self.check_connect()
                self.handle_connect()
            self.handle_read()
    
    def handle_write_event(self):
        if self.accepting:
            # Should never get a write event, but if we do, throw
            # it away
            return
        else:
            # Getting a write implies that we are connected, so
            # same logic as for handle_read_event above
            if not self.connected:
                self.check_connect()
                self.handle_connect()
            self.handle_write()
    
    def close(self):
        # This is the method that should be called from all the
        # places that call handle_close in asyncore.dispatcher
        self.del_channel()
        if not self.closed:
            self.handle_close()
            self.connect_pending = False
        SocketIOBase.close(self)
    
    def handle_accept(self):
        """Should only be implemented in servers.
        """
        raise NotImplementedError
    
    def handle_connect(self):
        self.on_connect()
    
    def on_connect(self):
        """Placeholder for derived classes.
        """
        pass

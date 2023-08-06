#!/usr/bin/env python
"""
Module SOCKET -- Socket I/O Handling
Sub-Package IO.SOCKET of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module implements socket-specific I/O functionality
that is useful in both blocking and non-blocking modes.
"""

import os
import socket
from errno import EPIPE, ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, \
    EISCONN, EBADF, errorcode

from plib.io.base import BaseData, BaseIO

connect_confirm_values = [0, EISCONN]

socket_close_errors = [EPIPE, ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED]

socket_close_confirm_errors = [EBADF] + socket_close_errors


class SocketIOBase(BaseIO):
    """Base class for socket I/O functionality.
    
    Overlays the underlying socket object methods with error
    checking and handling.
    """
    
    accepting = False
    addr = None
    closed = True
    connected = False
    
    def __init__(self, sock=None):
        if sock:
            try:
                self.addr = sock.getpeername()
                self.connected = True # will only get here if connected
            except socket.error, err:
                if err[0] == ENOTCONN:
                    # To handle the case where we got an unconnected
                    # socket; self.connected is False by default
                    pass
                else:
                    raise
            self.set_socket(sock)
        else:
            self.socket = None
    
    def create_socket(self, family, type):
        self.set_socket(socket.socket(family, type))
    
    def set_socket(self, sock):
        self.socket = sock
        self.closed = False
    
    def set_reuse_addr(self):
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR) | 1)
        except socket.error:
            pass
    
    def listen(self, num):
        self.accepting = True
        if os.name == 'nt' and num > 5:
            num = 1
        return self.socket.listen(num)
    
    def bind(self, addr):
        self.addr = addr
        return self.socket.bind(addr)
    
    def accept(self):
        return self.socket.accept()
    
    def connect_confirmed(self, value):
        """Check if return value confirms connect succeeded.
        """
        return value in connect_confirm_values
    
    def connect(self, address):
        self.connected = False
        err = self.socket.connect_ex(address)
        # FIXME: Add Winsock return values?
        if self.connect_confirmed(err):
            self.addr = address
            self.connected = True
            self.closed = False
        else:
            raise socket.error, (err, errorcode[err])
    
    def keep_open_on_exc(self, why):
        """Allow derived classes to keep socket open on certain errors.
        """
        return False
    
    def socket_close_ok(self, err):
        """Certain errors should not raise exception after socket close.
        """
        return err in socket_close_errors
    
    def send(self, data):
        try:
            return self.socket.send(data)
        except socket.error, why:
            if self.keep_open_on_exc(why):
                return 0
            self.close()
            if self.socket_close_ok(why[0]):
                return 0
            else:
                raise
    
    def recv(self, buffer_size):
        try:
            # NOTE: A recv of zero bytes means the socket on the other end has
            # closed, so you might think we'd check for that here and call
            # ``self.close()`` if it happens; however, doing that would break
            # a read/write strategy that let the other end call ``shutdown``
            # when it was finished sending but could still receive (e.g., see
            # the ``ShutdownReadWrite`` class). So we need to leave it to
            # higher-level code (mainly the read/write handling classes) to
            # decide how to handle zero-byte reads.
            return self.socket.recv(buffer_size)
        except socket.error, why:
            if self.keep_open_on_exc(why):
                return ''
            self.close()
            if self.socket_close_ok(why[0]):
                return ''
            else:
                raise
    
    def socket_close_confirm(self, err):
        """Certain errors on socket close attempt should not raise exception.
        
        These errors just confirm that the socket is already closed.
        """
        return err in socket_close_confirm_errors
    
    # BaseIO method implementations
    
    def dataread(self, bufsize):
        return self.recv(self.bufsize)
    
    def datawrite(self, data):
        return self.send(self.write_data)
    
    def close(self):
        # The closed flag ensures that we only go through the
        # actual socket close procedure once (assuming it succeeds),
        # even if we are called multiple times from different
        # trigger events; note that calling socket.close() may not
        # throw an exception even if called on an already closed
        # socket, so we can't use the except clause as our test for
        # being already closed
        if not self.closed:
            self.accepting = False
            self.connected = False
            try:
                self.socket.close()
                self.closed = True
            except socket.error, why:
                if self.socket_close_confirm(why[0]):
                    self.closed = True
                else:
                    raise


class SocketData(BaseData):
    """Basic data handling for socket I/O.
    """
    
    bufsize = 4096

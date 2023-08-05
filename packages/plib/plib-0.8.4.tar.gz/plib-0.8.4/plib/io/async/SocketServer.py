#!/usr/bin/env python
"""
Module SocketServer
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous SocketServer class.
It provides an alternative to the standard socket servers
in the Python standard library (or in the ``blocking``
sub-package of this library), using non-blocking,
asynchronous I/O.
"""

from functools import partial

from plib.io.mixins import SelfPipe, SelfPipeServerMixin
from plib.io.socket import BaseServer
from plib.io.async import AsyncBase, SocketDispatcher


class _AsyncSelfPipe(SelfPipe, AsyncBase):
    # Internal class specializing SelfPipe for our async API
    
    def __init__(self, callback):
        SelfPipe.__init__(self, callback)
        AsyncBase.__init__(self)
        # This works because SelfPipe overrides the fileno method
        self.set_fileobj(self)
    
    def handle_read(self):
        # This will trigger the callback for each signal received
        # (AsyncBase default is to always be readable, so
        # the pipe will be checked on every select/poll call)
        self.receive_signals()
    
    def writable(self):
        # The pipe shouldn't appear as writable to select/poll
        return False


# We make a partial of one of these for the keep_running check;
# which one depends on whether a callback is passed to serve_forever
# (we need a partial either way because do_loop needs a callback)

def keep_running_callback(self, callback):
    c = callback()
    if self.keep_running():
        return c
    return False


def keep_running_no_callback(self):
    if not self.keep_running():
        return False


class SocketServer(SelfPipeServerMixin, BaseServer, SocketDispatcher):
    """Base class for async socket server.
    
    Dispatches an instance of its handler class to handle each
    request. Pretty much a functional equivalent to the Python
    standard library ``SocketServer``, but using async I/O.
    
    Uses the self-pipe trick to be notified of signals that
    should break out of the ``serve_forever`` loop.
    """
    
    pipe_class = _AsyncSelfPipe
    
    def __init__(self, server_addr, handler_class):
        SocketDispatcher.__init__(self)
        BaseServer.__init__(self, server_addr, handler_class)
    
    def handle_accept(self):
        self.on_accept()
        conn, addr = self.accept()
        self.handler(conn, addr, self)
    
    def on_accept(self):
        """Placeholder for derived classes.
        """
        pass
    
    def close(self):
        if not self.closed:
            self.server_close()
        super(SocketServer, self).close()
    
    def server_loop(self, callback=None):
        if callback is not None:
            f = partial(keep_running_callback,
                self, callback)
        else:
            f = partial(keep_running_no_callback,
                self)
        self.do_loop(f)

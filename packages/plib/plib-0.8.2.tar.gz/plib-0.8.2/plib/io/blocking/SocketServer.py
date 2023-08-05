#!/usr/bin/env python
"""
Module SocketServer
Sub-Package IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a simplified alternate to the SocketServer
class from the Python standard library. This class is not very
useful in itself (like the Python standard library equivalent)
because it can only handle one request at a time; but it also
serves as a common base class for the more useful blocking
socket servers, ``ForkingServer`` and ``ThreadingServer``.
All three of these classes, collectively, are discussed in
the following.

The key changes from the Python standard library are:

- Simpler method structure (based on the general I/O methods
  used by all modules in this sub-package)
  
- Only TCP INET servers are included, since these classes
  are intended to be fully portable (so no Unix sockets are
  included), and since UDP support is difficult to get working
  on Linux.
  
- The forking server by default sets its SIGCHLD handler to
  SIG_IGN (on platforms that have SIGCHLD). This means the
  kernel will take care of reaping zombie children when they
  exit, so our code doesn't have to worry about it. If more
  control over child processes is needed, a mixin class is
  available, ``SigChldServerMixin``, which adds SIGCHLD
  handling functionality.
  
- It is possible to set a timeout while listening for requests
  (as is done in Python 2.6 and later), but there is none by
  default, since one shouldn't be needed. As far as I can tell,
  the reason for adding the timeout functionality in Python
  2.6 was to support PyGTK, but I have a hard time seeing why
  you'd want to run a server in the same process as a GUI event
  loop. Servers are *supposed* to be run in their own processes;
  a GUI to make use of the server's functionality should be a
  *client*, talking to the server through a socket. (And if you
  want to do that with a client, the client should be using
  asynchronous I/O anyway--see the client classes in the
  plib.io.async sub-package.)
  
- No attempt is made to allow the server to be shut down by a
  method call from another thread. The only place multiple
  threads are used in this library is the threading server, and
  the only threads it spawns are request handlers, which should
  not be able to shut down the server with a method call. In
  any case, servers shouldn't be running in processes which have
  multiple threads doing other things that might shut the server
  process down; those things should be done in their own
  separate processes, talking to the server through a socket...
"""

import os
import select
import signal
import socket
from errno import EINTR
from functools import partial

try:
    from errno import ERESTART # won't work on OS X
except ImportError:
    ERESTART = None # safe alternate

from plib.io.mixins import SelfPipeServerMixin
from plib.io.socket import BaseServer, SocketIOBase


# We make a partial of this for the keep_running check if a
# callback is passed to serve_forever

def keep_running_callback(self, callback):
    c = callback()
    return self.keep_running() and (c is not False)


class SocketServer(SelfPipeServerMixin, BaseServer, SocketIOBase):
    """Blocking TCP server base class.
    
    Uses the self-pipe trick to be notified of signals that
    should break out of the ``serve_forever`` loop. The select
    call is added to ``server_loop`` to facilitate this. A
    timeout can be specified with the ``poll_timeout`` class
    field, but there is none by default (which is desirable
    because of the inefficiency of cycling the loop when nothing
    is happening).
    """
    
    poll_timeout = None
    
    def __init__(self, server_addr, handler_class):
        SocketIOBase.__init__(self)
        BaseServer.__init__(self, server_addr, handler_class)
    
    def start_child(self, handler, conn, addr):
        """Start a "child" to handle a request.
        
        This default implementation simply runs the handler
        synchronously in the same process. Derived classes
        override to either fork a new process or start a new
        thread to run the handler, for concurrency.
        """
        try:
            handler(conn, addr, self)
        except:
            self.handle_error()
    
    def handle_accept(self):
        """Get the request info and start a handler.
        """
        self.on_accept()
        conn, addr = self.accept()
        self.start_child(self.handler, conn, addr)
    
    def on_accept(self):
        """Placeholder for derived classes.
        """
        pass
    
    def close(self):
        if not self.closed:
            self.server_close()
            self.handle_close()
        super(SocketServer, self).close()
    
    def handle_close(self):
        self.on_close()
    
    def on_close(self):
        """Placeholder for derived classes.
        """
        pass
    
    def server_loop(self, callback=None):
        if callback is not None:
            _keep_running = partial(keep_running_callback,
                self, callback)
        else:
            _keep_running = self.keep_running
        while _keep_running():
            try:
                pipe_fd = self.pipe.fileno()
                sock_fd = self.socket.fileno()
                r, w, e = select.select([pipe_fd, sock_fd],
                    [], [], self.poll_timeout)
                if pipe_fd in r:
                    # This triggers self.signal_callback for each signal
                    self.pipe.receive_signals()
                elif sock_fd in r:
                    # Only try accepting if pipe wasn't read
                    self.handle_accept()
            except (socket.error, select.error), why:
                # If we get an 'interrupted system call', don't shut
                # down, just re-start the call after checking
                # keep_running to see if the interruption was a
                # terminate signal
                if why[0] in (EINTR, ERESTART):
                    continue
                else:
                    raise

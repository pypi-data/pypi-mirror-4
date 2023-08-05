#!/usr/bin/env python
"""
CHAT_SERVER.PY
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Python implementation of a "chat" server, which can have
multiple "clients", each of which sees messages sent by all
the others. The chat client and server both demonstrate
simple but illustrative use cases for the asynchronous
"persistent" I/O classes in ``plib.io.async``.
Key aspects of the server:

- The "asynchronous" part: this server has to maintain
  common state between multiple request handlers, since each
  handler has to pass on its messages to all the others.
  This is simple with an async server, as you can see from
  the code below. A forking server would have to somehow
  implement message passing between handlers and the server,
  which would require, at the least, extra sockets (or pipes,
  or some other IPC mechanism), and would impose a lot of overhead
  on what is essentially a simple thing. Even a threading
  server, which could provide shared state between handlers,
  would have to protect that state with mutexes so multiple
  handlers could not mutate it at the same time.

- The "persistent" part: each handler has to interleave reading
  messages from its client, and passing them on, with sending
  messages from all the other handlers to its client. Since
  these things can happen at arbitrary times, the handler can't
  make any assumptions about which type of I/O will happen in
  what order, as a normal request handler would. This is the
  type of use case that the "persistent" I/O classes in this
  library are meant for.
"""

import sys
import os
import signal

from plib.io.mixins import SigIntServerMixin
from plib.io.async import (
    PersistentRequestHandlerWithTerminator, SocketServer)


class ChatRequestHandler(PersistentRequestHandlerWithTerminator):
    """Test chat request handler.
    
    Writes initial greeting message before starting
    round-trip data exchange.
    
    Echoes data received to stdout and to all other clients.
    """
    
    terminator = os.linesep  # so tools like netcat can talk to us
    
    handlers = []  # easy hack to avoid a global variable
    
    def on_connect(self):
        sys.stdout.write("Chat server accepted connection.%s" %
            self.terminator)
        # TerminatorReadWrite will automatically add
        # the line break when sending to client
        self.start("Connected to chat server.")
        # We'll now start getting chat lines from other clients
        self.handlers.append(self)
    
    def process_data(self):
        if self.read_data:
            # Add back line break when writing to stdout
            # since TerminatorReadWrite strips it
            sys.stdout.write("%s%s" % (self.read_data, self.terminator))
        for handler in self.handlers:
            if handler is not self:
                handler.start(self.read_data)
    
    def on_close(self):
        self.handlers.remove(self)
        sys.stdout.write("Chat server connection closed.%s" %
            self.terminator)


class ChatServer(SigIntServerMixin, SocketServer):
    """Test chat server.
    
    Adds some status messages to stdout for testing.
    
    Exits on Ctrl-C, neatly (i.e., without the messy traceback
    that Python would print if we used the default of letting
    Ctrl-C raise a KeyboardInterrupt).
    """
    
    allow_reuse_address = True
    term_sigs = SigIntServerMixin.term_sigs + [signal.SIGTERM]
    
    def serve_forever(self):
        sys.stdout.write("Chat server listening.%s" %
            ChatRequestHandler.terminator)
        super(ChatServer, self).serve_forever()
    
    def server_close(self):
        super(ChatServer, self).server_close()
        sys.stdout.write("Chat server exiting.%s" %
            ChatRequestHandler.terminator)


if __name__ == '__main__':
    ChatServer(("localhost", 9999), ChatRequestHandler).serve_forever()

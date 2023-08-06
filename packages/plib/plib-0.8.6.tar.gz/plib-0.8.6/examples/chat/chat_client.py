#!/usr/bin/env python
"""
CHAT_CLIENT.PY
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Python implementation of a "chat" client, which reads
input from stdin and sends it to a chat server, and gets
data sent from the server and displays it. The chat
client and server both demonstrate simple but illustrative
use cases for the asynchronous "persistent" I/O classes
in ``plib.io.async``. Key aspects of the client:

- The "asynchronous" part: this client multiplexes reading
  the user's typed messages on standard input with socket
  I/O, and both types of input can arrive at any time. This
  type of I/O is virtually impossible to handle with blocking
  reads--certainly not while keeping the user interface
  responsive. In principle threads could be used to keep the
  UI responsive while socket I/O was taking place, and vice
  versa, but then you would have to have a mechanism for
  passing the data read from stdin in the UI thread to the
  socket I/O thread for writing to the socket, which brings
  in all the well-known issues with mutexes, etc. This client
  neatly avoids all of that.

- The "persistent" part: the client may have to write user
  messages to the socket interleaved in arbitrary order with
  reading chat messages coming from the server. A normal
  "client" implementation has to make assumptions about when
  and in what order the two types of I/O, reading and writing,
  will occur. This client does not; it simply handles whatever
  happens, in the order in which it happens.
"""

import sys
import os

from plib.io.async import (
    AsyncBase, PersistentSocketWithTerminator)


class AsyncStdin(AsyncBase):
    
    def __init__(self, chat):
        AsyncBase.__init__(self)
        self.chat = chat
        self.i = sys.stdin
        self.set_fileobj(sys.stdin)
    
    def writable(self):
        # Can't write to standard input!
        return False
    
    def readable(self):
        # This disables reading user input until the greeting is received
        return self.chat.greeting_received
    
    def handle_read(self):
        self.chat.stdin_data(self.i.readline())


class ChatClient(PersistentSocketWithTerminator):
    """Chat client for testing.
    
    Waits for greeting message when first connecting. Prints all
    received data to stdout. Exits on Ctrl-C or EOF (Ctrl-D),
    or by typing "QUIT".
    """
    
    terminator = os.linesep
    
    server_addr = ("localhost", 9999)
    QUIT = "QUIT"
    
    greeting_received = False
    
    def on_connect(self):
        print "Got connection!"
        self.async_stdin = AsyncStdin(self)
    
    def writable(self):
        # This disables sending data until the greeting is received
        return self.greeting_received and super(ChatClient, self).writable()
    
    def process_data(self):
        print self.read_data
        if not self.greeting_received:
            self.greeting_received = True
    
    def stdin_data(self, data):
        if data == self.QUIT:
            raise EOFError("QUIT received")
        self.start(data)
    
    def run(self):
        # Run interactive session
        try:
            self.do_connect(self.server_addr)
            self.do_loop()
        except (KeyboardInterrupt, EOFError):
            self.close()
    
    def on_close(self):
        self.async_stdin.close()
        print "Closing connection!"


if __name__ == '__main__':
    ChatClient().run()

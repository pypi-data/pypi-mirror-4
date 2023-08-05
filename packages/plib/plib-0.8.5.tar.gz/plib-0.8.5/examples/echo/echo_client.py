#!/usr/bin/env python
"""
ECHO_CLIENT.PY
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Python implementation of an "echo" client, which reads
input from stdin and sends it to an "echo" server that
just sends the same data back. Received data is printed
to stdout.

This class illustrates the use of the ``PClientBase``
class in ``plib.io.classes``, which provides a simple way
of sending requests to servers and getting replies back.
It also illustrates how the ``plib.io`` library
is set up to allow easy switching between different I/O
types (async and blocking)--even, as in this case,
switching at runtime based on a command line argument.
"""

import sys
import os

from plib.io.classes import PClientBase
from plib.stdlib.imp import import_from_module

if (len(sys.argv) > 1):
    iotype = sys.argv[1]
else:
    iotype = 'blocking'

SocketClientWithTerminator = import_from_module(
    'plib.io.%s' % iotype, "SocketClientWithTerminator")


class EchoClient(PClientBase, SocketClientWithTerminator):
    """Echo client for testing (something like netcat).
    
    Waits for greeting message when first connecting. Prints all
    received data to stdout. Exits on Ctrl-C or EOF (Ctrl-D),
    or by typing "QUIT".
    """
    
    keep_alive = True
    terminator = os.linesep
    
    server_addr = ("localhost", 7000)
    QUIT = "QUIT"
    
    greeting_received = False
    
    def on_connect(self):
        print "Got connection!"
    
    def process_data(self):
        super(EchoClient, self).process_data()
        if not self.greeting_received:
            self.greeting_received = True
    
    def setup_client(self, client_id):
        super(EchoClient, self).setup_client(client_id)
        self.wait_for(self, 'greeting_received')
    
    def run(self):
        # Run interactive session (the constructor
        # has already connected us)
        try:
            while 1:
                data = raw_input()
                if data == self.QUIT:
                    self.close()
                    break
                print self(data)
        except (KeyboardInterrupt, EOFError):
            self.close()
    
    def on_close(self):
        print "Closing connection!"


if __name__ == '__main__':
    EchoClient().run()

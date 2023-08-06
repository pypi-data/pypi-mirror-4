#!/usr/bin/env python
"""
Module CHATGEN -- Generator wrappers for client/server I/O
Sub-Package IO of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``chat_replies`` class, which wraps an
asynchronous socket client so it looks like a generator. For
an example of usage, see the ``pyidserver.py`` example program.
"""

from plib.stdlib.coll import fifo

from plib.io.async import SocketClient


class chat_replies(SocketClient):
    """Data exchange of list of items as a generator.
    
    Generator that sends data items to a server one by one
    and yields the replies.
    """
    
    keep_alive = True
    
    def __init__(self, addr, items, callback=None):
        self.server_addr = addr
        self.callback = callback
        self.data_queue = fifo(items)
        super(chat_replies, self).__init__()
    
    def start(self, data):
        self.reply = None
        if data is not None:
            super(chat_replies, self).start(data)
    
    def process_data(self):
        self.reply = self.read_data
    
    def do_loop(self, callback=None):
        if callback is not None:
            if self.callback is not None:
                c = self.callback
                def f():
                    c1 = c()
                    c2 = callback()
                    if (c1 is False) or (c2 is False):
                        return False
            else:
                f = callback
        else:
            f = self.callback
        super(chat_replies, self).do_loop(f)
    
    def __iter__(self):
        try:
            self.setup_client(self.server_addr)
            while self.data_queue and not self.closed:
                self.client_communicate(self.data_queue.next())
                if self.reply is None:
                    # If we didn't get any data back, exit the generator
                    break
                else:
                    yield self.reply
        finally:
            self.close()

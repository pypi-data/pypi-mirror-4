#!/usr/bin/env python
"""
TEST_IO_CHATGEN.PY -- test script for chatgen module
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the chatgen module of
plib.io.
"""

import unittest

from plib.io.mixins import EchoRequestMixin
from plib.io.async import PersistentRequestHandler, SocketServer
from plib.io.classes import chat_replies

from io_testlib import IOServerMixin, IOChannelTest


class ChatHandler(EchoRequestMixin, PersistentRequestHandler):
    pass


class ChatServer(IOServerMixin, SocketServer):
    pass


class ChatTestMixin(object):
    
    handler_class = ChatHandler
    server_class = ChatServer


class ChatClientTest(ChatTestMixin, IOChannelTest, unittest.TestCase):
    
    def test_chat_client(self):
        seq = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
        results = [reply for reply in chat_replies(
            ('localhost', self.server_port), seq)]
        self.assertEqual(results, seq)


def testcallback():
    pass


class ChatClientTestCallback(ChatTestMixin, IOChannelTest, unittest.TestCase):
    
    def test_chat_callback(self):
        seq = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]
        results = [reply for reply in chat_replies(
            ('localhost', self.server_port), seq, testcallback)]
        self.assertEqual(results, seq)


start_msg = "Started!"


class ChatHandlerNone(ChatHandler):
    
    def __init__(self, request, client_address, server):
        ChatHandler.__init__(self, request, client_address, server)
        self.start(start_msg)


class ChatClientTestWithNone(ChatTestMixin, IOChannelTest, unittest.TestCase):
    
    handler_class = ChatHandlerNone
    
    def test_chat_client(self):
        seq = [None, "Python rocks!", "Try it today!", "You'll be glad you did!"]
        results = [reply for reply in chat_replies(
            ('localhost', self.server_port), seq)]
        self.assertEqual(results, [start_msg] + seq[1:])


if __name__ == '__main__':
    unittest.main()

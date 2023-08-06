#!/usr/bin/env python
"""
TEST_IO_API.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests checking details of the external API for
the I/O modules in the PLIB.STDLIB sub-package.
"""

import unittest

from io_testlib import IOChannelTest
from io_testlib_async import AsyncHandler, AsyncServer
from io_testlib_async import SocketClient as _AsyncClient
from io_testlib_blocking import BlockingHandler, BlockingServer
from io_testlib_blocking import SocketClient as _BlockingClient


class RestartMixin(object):
    
    restarted = False
    result = ""
    
    def client_communicate(self, data, client_id=None, callback=None):
        self.restarted = False
        self.result = ""
        super(RestartMixin, self).client_communicate(data,
            client_id, callback)
    
    def process_data(self):
        if self.restarted:
            self.result = self.read_data
        else:
            self.start(self.read_data)
            self.restarted = True


class AsyncClient(RestartMixin, _AsyncClient):
    pass


class AsyncTestMixin(IOChannelTest):
    
    client_class = AsyncClient
    handler_class = AsyncHandler
    server_class = AsyncServer


class BlockingClient(RestartMixin, _BlockingClient):
    pass


class BlockingTestMixin(IOChannelTest):
    
    client_class = BlockingClient
    handler_class = BlockingHandler
    server_class = BlockingServer


class APIMixin(object):
    
    test_data = "Python rocks!"
    
    def get_client(self):
        client = self.client_class()
        client.setup_client(('localhost', self.server_port))
        return client
    
    def do_client_comm(self, client):
        client.client_communicate(self.test_data)
        self.assert_(client.restarted)
        self.assertEqual(client.result, self.test_data)


class RestartTestMixin(APIMixin):
    
    def test_restart(self):
        # Test that calling ``start`` inside the communication
        # loop keeps it open, even if ``keep_alive`` is false
        # on the client side; but once there is no more data,
        # the client closes.
        client = self.get_client()
        self.do_client_comm(client)
        self.assert_(client.closed)


class BlockingRestartTest(RestartTestMixin, BlockingTestMixin, unittest.TestCase):
    pass


class AsyncRestartTest(RestartTestMixin, AsyncTestMixin, unittest.TestCase):
    pass


class KeepAliveTestMixin(APIMixin):
    
    tries = 2
    
    def test_restart_keepalive(self):
        # Test that a client with ``keep_alive`` true can be
        # restarted without re-connecting, as long as finish
        # has not been called from user code (note that there
        # is no such call in the ``process_data`` method of
        # the client).
        client = self.get_client()
        client.keep_alive = True
        for _ in xrange(self.tries):
            self.do_client_comm(client)
        self.assert_(not client.closed)
        client.close()
        self.assert_(client.closed)


class BlockingKeepAliveTest(KeepAliveTestMixin, BlockingTestMixin, unittest.TestCase):
    pass


class AsyncKeepAliveTest(KeepAliveTestMixin, AsyncTestMixin, unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()

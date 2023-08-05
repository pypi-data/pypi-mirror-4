#!/usr/bin/env python
"""
TEST_IO_MULTIREQUEST.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests to ensure that the I/O servers in the
PLIB.STDLIB sub-package can handle multiple requests, both in sequence
and concurrent.
"""

import sys
import time
import unittest
from functools import partial

from io_testlib import ConcurrentRequestTest, MultiRequestTest
from io_testlib_async import AsyncClient, AsyncHandler, AsyncServer
from io_testlib_blocking import (BlockingClient, BlockingHandler,
    ThreadingServer)

if sys.platform != 'win32':
    # The forking server currently does not work on Windows
    from io_testlib_blocking import ForkingServer


# For blocking I/O, implement delay by having each request
# handler call sleep before processing data

class SleepingHandler(BlockingHandler):
    
    def process_data(self):
        time.sleep(0.5)
        super(SleepingHandler, self).process_data()


if sys.platform != 'win32':
    
    class ForkingTestMixin(object):
        
        client_class = BlockingClient
        server_class = ForkingServer
    
    
    class ForkingConcurrentRequestTest(ForkingTestMixin,
            ConcurrentRequestTest, unittest.TestCase):
        
        handler_class = SleepingHandler
    
    
    class ForkingConcurrentRequestTestWithGoCode(ForkingTestMixin,
            ConcurrentRequestTest, unittest.TestCase):
        
        handler_class = BlockingHandler
        use_gocode = True
    
    
    class ForkingMultiRequestTest(ForkingTestMixin,
            MultiRequestTest, unittest.TestCase):
        
        handler_class = BlockingHandler


class ThreadingTestMixin(object):
    
    client_class = BlockingClient
    server_class = ThreadingServer


class ThreadingConcurrentRequestTest(ThreadingTestMixin,
        ConcurrentRequestTest, unittest.TestCase):
    
    handler_class = SleepingHandler


class ThreadingConcurrentRequestTestWithGoCode(ThreadingTestMixin,
        ConcurrentRequestTest, unittest.TestCase):
    
    handler_class = BlockingHandler
    use_gocode = True


class ThreadingMultiRequestTest(ThreadingTestMixin,
        MultiRequestTest, unittest.TestCase):
    
    handler_class = BlockingHandler


# For async I/O, since the handlers can't block the overall
# communication loop, implement delay by having the master
# loop keep track of paused handlers

paused_handlers = {}


class PausingHandler(AsyncHandler):
    
    paused = ""
    
    def process_data(self):
        global paused_handlers
        self.paused = self.read_data
        paused_handlers[self._fileno] = (time.time(), self)
    
    def unpause(self):
        global paused_handlers
        del paused_handlers[self._fileno]
        self.start(self.paused)
        self.paused = ""


def pause_callback(self, callback):
    result = callback()
    if (result is not False) and paused_handlers:
        self.check_paused_handlers()
    return result


def pause_no_callback(self):
    if paused_handlers:
        self.check_paused_handlers()


class PausingServer(AsyncServer):
    
    poll_timeout = 0.5
    
    def check_paused_handlers(self):
        unpaused = []
        for key, value in paused_handlers.iteritems():
            t, handler = value
            if time.time() > (t + 0.5):
                unpaused.append(handler)
        for handler in unpaused:
            handler.unpause()
    
    def do_loop(self, callback=None):
        if callback is not None:
            f = partial(pause_callback, self, callback)
        else:
            f = partial(pause_no_callback, self)
        super(PausingServer, self).do_loop(f)


class NonBlockingConcurrentRequestTest(ConcurrentRequestTest,
        unittest.TestCase):
    
    client_class = AsyncClient
    handler_class = PausingHandler
    server_class = PausingServer


class NonBlockingConcurrentRequestTestWithGoCode(ConcurrentRequestTest,
        unittest.TestCase):
    
    client_class = AsyncClient
    handler_class = AsyncHandler
    server_class = AsyncServer
    use_gocode = True


class NonBlockingMultiRequestTest(MultiRequestTest,
        unittest.TestCase):
    
    client_class = AsyncClient
    handler_class = AsyncHandler
    server_class = AsyncServer


if __name__ == '__main__':
    if sys.platform == 'win32':
        print "Forking server disabled, skipping forking multi-request tests."
    unittest.main()

#!/usr/bin/env python
"""
IO_TESTLIB_PERSISTENT.PY -- utility module for PLIB.STDLIB I/O tests
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common code for the tests of the persistent async
I/O modules in PLIB.STDLIB.
"""

from plib.io.async import (SocketServer,
    PersistentSocketWithReadWrite, PersistentRequestHandlerWithReadWrite,
    PersistentSocketWithTerminator, PersistentRequestHandlerWithTerminator)

from io_testlib import (PersistentIOClientMixin,
    PersistentIOHandlerMixin, PersistentIOServerMixin)


class AsyncServer(PersistentIOServerMixin, SocketServer):
    pass


class ReadWriteClient(PersistentIOClientMixin,
        PersistentSocketWithReadWrite):
    pass


class ReadWriteHandler(PersistentIOHandlerMixin,
        PersistentRequestHandlerWithReadWrite):
    pass


class ReadWriteTestMixin(object):
    
    client_class = ReadWriteClient
    handler_class = ReadWriteHandler
    server_class = AsyncServer


class TerminatorClient(PersistentIOClientMixin,
        PersistentSocketWithTerminator):
    pass


class TerminatorHandler(PersistentIOHandlerMixin,
        PersistentRequestHandlerWithTerminator):
    pass


class TerminatorTestMixin(object):
    
    client_class = TerminatorClient
    handler_class = TerminatorHandler
    server_class = AsyncServer

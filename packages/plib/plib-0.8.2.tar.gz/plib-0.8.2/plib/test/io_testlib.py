#!/usr/bin/env python
"""
IO_TESTLIB.PY -- utility module for PLIB.STDLIB I/O tests
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common code for the tests of the I/O
modules in PLIB.STDLIB.
"""

import sys
import os
import signal
import socket
from errno import EPIPE, ECONNRESET
from functools import partial

from plib.stdlib.coll import fifo
from plib.stdlib.comm._processwrapper import ProcessWrapper
from plib.stdlib.comm._serverproxy import ServerProxy
from plib.stdlib.comm._socketwrapper import socketpair_wrapper

# FIXME: make this work on Windows
#if sys.platform == 'win32':
#    # Use threads for multi-client concurrent request tests
#    # (child processes are way too slow on Windows)
#    from plib.stdlib.comm._threadwrapper import ThreadWrapper


# Helper function to read all available data from a socket
# (note that this function assumes that the other end will
# close its socket when it is finished sending data--i.e.,
# this function can only be used as the last data transfer
# on a socket)

def recv_all(sock, bufsize=4096):
    result = ""
    while 1:
        s = sock.recv(bufsize)
        if not s:
            break
        result += s
    return result


# Server mixin class (currently just a placeholder in case we
# want to add common server functionality in future)

class IOServerMixin(object):
    pass


# Run the server listening on an ephemeral port, and send the port
# number back to the test case through a socket pair (using an
# ephemeral port ensures no port collisions between successive
# tests); we use ServerProxy so (<module_name>, <class_name>) tuples
# can be used for the server and handler classes

def run_io_server(server_class, handler_class, sock):
    proxy = ServerProxy(server_class, ('localhost', 0), handler_class)
    proxy.start_server()
    iface, port = proxy.server.socket.getsockname()
    sock.sendall(str(port))
    sock.close()
    proxy.run_server()


# Fork a server and get its port number back through a socket pair
# (yes, we could use a pipe on Unix-type systems, since the data
# flow is one-way, but we don't want to have to special-case this
# code for different platforms, and we have a socketpair emulation
# already implemented for Windows)

def fork_server_with_port(server_class, handler_class):
    sock, server = socketpair_wrapper(
        partial(run_io_server, server_class, handler_class),
        ProcessWrapper)
    portstr = recv_all(sock)
    sock.close()
    return server, int(portstr)


# Base class for all I/O channel tests, contains common
# code to fork and manage the I/O server.

class IOChannelTest(object):
    
    handler_class = None
    server_class = None
    
    server = None
    server_port = None
    
    def setUp(self):
        # We allow for fork issues that are unrelated to our tests;
        # but three failures is enough to assume that there is a
        # genuine problem with the server class
        tries = 0
        while self.server is None:
            try:
                self.server, self.server_port = fork_server_with_port(
                    self.server_class,
                    self.handler_class)
            except IOError, e:
                tries += 1
                msg = str(e)
                if (msg != "fork_wait aborted!") or (tries >= 3):
                    raise
    
    def tearDown(self):
        # We check the server field so that we won't try to kill
        # the server if it's already been closed by a test
        if self.server is not None:
            self.server.end()
            self.server = None


# Client that keeps track of multiple round-trip data exchanges
# and flags early closing of the I/O channel; note that the same
# mixin class works for all I/O types (and similarly for request
# handlers and servers)

class IOClientMixin(object):
    
    result = ""
    trips_required = 1
    trips_completed = 0
    
    def trips_done(self):
        return self.trips_completed >= self.trips_required
    
    def process_data(self):
        self.trips_completed += 1
        if self.trips_done():
            # This ensures that the test won't pass until all
            # required round trips are completed
            self.result = self.read_data
            if self.keep_alive:
                # This closes the client channel after multiple trips
                # (since it won't close automatically); note that the
                # server-side channel will see the close and close
                # itself, we don't need to subclass any code there
                self.finish()
    
    def close(self):
        # First make sure we clean up
        super(IOClientMixin, self).close()
        # This flags an error if we close before the trips are
        # completed (to make sure we do indeed keep our channel
        # alive for all the trips); note that we check first to
        # make sure no other exception is being handled (if one
        # is, we don't want to clobber it)
        if not self.trips_done():
            if sys.exc_info() == (None, None, None):
                if self.keep_alive:
                    descr = "Keep-alive channel"
                else:
                    descr = "Channel"
                raise RuntimeError("%s closed early!" % descr)


# The basic test of client/server data exchange. Note that the same
# subclassing works for client, request handler, and server classes
# of all I/O types. Also note that we can test multiple round-trip
# data exchanges by increasing the number_of_trips field in the
# test case (which fills in the client's trips_requried field).

class ClientServerTest(IOChannelTest):
    
    client_class = None
    number_of_trips = 1
    test_data = "Python rocks!"
    
    def setUp(self):
        # Make sure we keep channels open for multiple trips
        self.client_class.trips_required = self.number_of_trips
        if self.number_of_trips > 1:
            for klass in (self.client_class, self.handler_class):
                klass.keep_alive = True
        super(ClientServerTest, self).setUp()
    
    def test_io(self):
        client = self.client_class()
        client.setup_client(('localhost', self.server_port))
        for _ in xrange(self.number_of_trips):
            client.client_communicate(self.test_data)
        self.assertEqual(client.result, self.test_data)


# This is to test proper behavior of the alternate read/write classes
# with small buffer sizes (meaning that the terminator or data size
# bytes may take multiple reads to arrive).

class SmallBufferTest(ClientServerTest):
    
    def setUp(self):
        for klass in (self.client_class, self.handler_class):
            klass.bufsize = 1
        super(SmallBufferTest, self).setUp()


# Here we want to test interleaved full-duplex reads and writes, so
# we have the server/request handler send back different data, except
# for the sentinel at the end.

test_done = "All done!"
test_failed = "Oops, missed some data!"


# We have two ways of priming the write queue, but only the first (i.e.,
# the one used when ``test_auto_push`` is False) should be used by
# actual user code (see the comments in the writable method and in
# PersistentTest below)

class PersistentTestIO(object):
    
    test_case = None
    data_queue = None
    send_list = None
    
    received_list = None
    
    def writable(self):
        # Prime the write queue if not yet primed (we do this
        # here because ``do_loop`` is only called on the client side;
        # the request handler is "run" by the server's ``do_loop``,
        # not its own, whereas this method gets called on both ends.
        # Note that after the first time through, ``send_list`` is
        # empty, so no more priming is done.
        while self.send_list:
            self.start(self.send_list.next())
        # This priming method tests the ``start`` method to make
        # sure it pushes if nothing is pushed, but in the right order;
        # we do this by popping the last item in the queue and then
        # calling ``start`` with it; this should re-append it to the
        # queue and then push the first queue item; note that this
        # condition is mutually exclusive from the above (we'll have a
        # send_list or a data_queue, but never both). Note also that
        # this configuration is what I tried to implement in the actual
        # library code (in the ``PersistentMixin.writable`` method),
        # but that caused issues that don't arise when we do it here;
        # I'm not sure why there's a difference, but it's not essential
        # to figure it out (see the comments in the library method).
        if self.write_complete() and self.data_queue:
            self.start(self.data_queue.pop())
        return super(PersistentTestIO, self).writable()
    
    def start(self, data):
        if self.write_data:
            wait_count = 1
        else:
            wait_count = 0
        if self.data_queue:
            wait_count += len(self.data_queue)
        super(PersistentTestIO, self).start(data)
        if self.test_case:
            # Check to make sure we pushed data if there was anything to push
            self.test_case.assertFalse(
                self.write_complete() and self.data_queue)
            # Check to make sure we pushed in the right order
            self.test_case.assert_(
                (wait_count == 0) == (self.write_data == data))
    
    def process_data(self):
        if self.received_list is None:
            self.received_list = []
        self.received_list.append(self.read_data)


# Client that closes its comm loop once status is received from the
# handler (note that persistent channels have to explicitly call
# finish to break out of the loop)

class PersistentIOClientMixin(PersistentTestIO):
    
    def process_data(self):
        super(PersistentIOClientMixin, self).process_data()
        if self.read_data in (test_done, test_failed):
            self.finish()


# Request handler that tests received vs. expected data and sends back
# the status

class PersistentIOHandlerMixin(PersistentTestIO):
    
    expected_list = None
    
    def process_data(self):
        if self.read_data == test_done:
            if self.received_list == self.expected_list:
                self.start(test_done)
            else:
                self.start(test_failed)
        else:
            super(PersistentIOHandlerMixin, self).process_data()


# Server class that fills in the appropriate handler fields (we can't
# just do it on the handler class directly in the test case because
# the classes may get re-used in multiple tests; once the server is
# forked it's OK because the change won't be seen in the parent)

class PersistentIOServerMixin(IOServerMixin):
    
    client_list = None
    server_list = None
    test_auto_push = False
    
    def __init__(self, server_addr, handler_class):
        handler_class.expected_list = self.client_list
        server_sends = fifo(self.server_list)
        if self.test_auto_push:
            handler_class.data_queue = server_sends
        else:
            handler_class.send_list = server_sends
        super(PersistentIOServerMixin, self).__init__(server_addr, handler_class)


class PersistentTest(IOChannelTest):
    
    client_class = None
    
    client_list = None
    server_list = None
    
    # NOTE: Some test cases set this to True to test the ``start`` method
    # (see the comment in ``PersistentTestIO.writable`` above), but actual
    # user code should not use this hack (i.e., should not declare a
    # ``data_queue`` class member, as ``IOHandlerFactory`` and
    # ``IOClientFactory`` do above when this field is True); ``data_queue``
    # is intended to be an internal variable only
    
    test_auto_push = False
    
    # Attributes that will be temporarily copied to the server class
    # for on-passing to the handler after forking
    
    server_attrs = ('client_list', 'server_list', 'test_auto_push')
    
    def setUp(self):
        # Set up the server to fill in the handler fields after forking
        for attrname in self.server_attrs:
            oldattrname = 'old_%s' % attrname
            setattr(self, oldattrname, getattr(self.server_class, attrname))
            setattr(self.server_class, attrname, getattr(self, attrname))
        super(PersistentTest, self).setUp()
    
    def tearDown(self):
        super(PersistentTest, self).tearDown()
        # Restore the server class fields to avoid clobbering other tests
        for attrname in self.server_attrs:
            oldattrname = 'old_%s' % attrname
            setattr(self.server_class, attrname, getattr(self, oldattrname))
    
    def test_io(self):
        client = self.client_class()
        client.test_case = self
        client_sends = fifo(self.client_list + [test_done])
        if self.test_auto_push:
            client.data_queue = client_sends
        else:
            client.send_list = client_sends
        # FIXME: Async connects won't always raise ECONNREFUSED here, sometimes
        # it won't be received until the first read occurs inside do_loop; is
        # there a way to make it always be raised here (for consistent semantics
        # of do_connect between async and blocking)?
        client.do_connect(('localhost', self.server_port))
        # The data is already queued, so just run the comm loop
        client.do_loop()
        self.assertEqual(client.received_list, self.server_list + [test_done])


# Helper function to determine workable number of multiple/concurrent requests

def sys_request_num():
    if sys.platform == 'darwin':
        # XXX Mac OS X socket accept seems a lot slower than Linux
        return 15
    if sys.platform.startswith('freebsd'):
        # Process limit defaults seem pretty low on FreeBSD
        return 10
    if sys.platform == 'win32':
        # *Everything* is slow and clunky on Windows
        return 5
    return 100


# Test the ability of the servers to handle multiple requests; first, we just
# run each client one at a time, so the requests come in serially (but the
# shutdown of one request handler may still overlap the start of the next)

def client_test(client_class, test_data, server_port):
    client = client_class()
    try:
        client.client_communicate(test_data, ('localhost', server_port))
        return client.result
    except Exception, e:
        return str(e)


class MultiRequestTest(ClientServerTest):
    
    def test_io(self):
        request_num = sys_request_num()
        results = []
        for i in xrange(request_num):
            results.append(client_test(self.client_class,
                self.test_data, self.server_port))
        self.assertEqual(results, [self.test_data] * request_num)


# Now test handling of concurrent requests; we do this by forking all our
# clients so they make requests simultaneously. We try this two ways, with
# and without a "go code" sent to each client by the master test object.
# With the go code, each client process connects immediately, but doesn't
# send data until the go code is received; this means the server is forced
# to maintain as many "waiting" requests as we have clients, until they
# start receiving go codes--but on the other hand, since each client wakes
# up to send its go code sequentially, the requests will be handled and
# closed in sequence, so the server will never see more than one closing
# child process at a time. Without the go code, each client connects and
# does its round-trip data exchange as soon as it forks; here we impose a
# delay on the server end by forcing each request handler to wait for 0.5
# seconds before returning its reply, to try to keep as many concurrent
# connections pending as possible, so that requests will be handled in
# parallel (and consequently the server will be handling more than one
# closing child process at a time). Since we're not sure which case is
# harder for the server to handle, we test both ways.

go_code = "1"


def f_go(client_class, test_data, server_port, sock):
    try:
        client = client_class()
        client.setup_client(('localhost', server_port))
        try:
            go = sock.recv(1)
            if go == go_code:
                try:
                    client.client_communicate(test_data)
                    sock.sendall(client.result)
                except Exception, e:
                    sock.sendall(str(e))
        finally:
            client.close()
    finally:
        sock.close()


def f_nogo(client_class, test_data, server_port, sock):
    try:
        result = client_test(client_class, test_data, server_port)
        sock.sendall(result)
    finally:
        sock.close()


def r(fsock, fchild, use_gocode, test_data):
    result = ""
    try:
        try:
            if use_gocode:
                fsock.sendall(go_code)
            result = recv_all(fsock)
        except socket.error, why:
            if why[0] not in (EPIPE, ECONNRESET):
                raise
    finally:
        fsock.close()
    exitcode = fchild.exitcode()
    return (exitcode, result)


def multi_client_test(client_class, test_data, server_port,
        use_gocode, wrapper_class):
    
    if use_gocode:
        f = f_go
    else:
        f = f_nogo
    fsock, fchild = socketpair_wrapper(
        partial(f, client_class, test_data, server_port),
        wrapper_class)
    return partial(r, fsock, fchild, use_gocode, test_data)


class ConcurrentRequestTest(ClientServerTest):
    
    use_gocode = False
    
    def setUp(self):
        # Make sure the server's listen queue is large enough so
        # connections won't be refused (this is probably overkill
        # as the queue shouldn't build up this high because most
        # of the connections should be accepted quickly, but we want
        # to make sure)
        self.server_class.request_queue_size = sys_request_num()
        super(ConcurrentRequestTest, self).setUp()
    
    def test_io(self):
        # FIXME: make this work on Windows
        ## Use threads on Windows since subprocesses are so slow;
        ## otherwise use child processes for each client
        #if sys.platform == 'win32':
        #    wrapper_class = ThreadWrapper
        #else:
        wrapper_class = ProcessWrapper
        request_num = sys_request_num()
        results = []
        for i in xrange(request_num):
            results.append(multi_client_test(
                self.client_class,
                self.test_data,
                self.server_port,
                self.use_gocode,
                wrapper_class))
        for i, result in enumerate(results):
            results[i] = result()
        self.assertEqual(results, [(0, self.test_data)] * request_num)

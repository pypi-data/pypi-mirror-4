#!/usr/bin/env python
"""
TEST_STDLIB_FORK.PY -- test script for forking functions
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the forking functions in
the plib.stdlib.comm sub-package.
"""

import os
import socket
import unittest
from errno import EPIPE, ECONNRESET

from plib.stdlib.comm.forkwait import fork_wait
from plib.stdlib.comm.socketpair import fork_socketpair


def dummy_fn():
    pass


def bad_fn():
    raise Exception


def forkwait_test(f1, f2):
    child = fork_wait(f1, f2)
    exitcode = child.exitcode()
    return exitcode


test_byte = "1"


def socket_fn(sock):
    try:
        s = sock.recv(len(test_byte))
        sock.sendall(s)
    finally:
        sock.close()


def bad_socket_fn(sock):
    try:
        raise Exception
    finally:
        sock.close()


def socketpair_test(f, use_except=False):
    sock, child = fork_socketpair(f)
    try:
        try:
            sock.sendall(test_byte)
            result = sock.recv(len(test_byte))
        except socket.error, why:
            # Catch expected error if child process throws exception
            # and closes its socket; this is a more precise test than
            # just using assertRaises(socket.error, ...) in the test
            # case (since that would catch all socket errors, not just
            # the ones we want). We'll test whether the child branch
            # of fork_socketpair exited correctly when we test its
            # exit code (should be 1 on any exception). Note that the
            # OS will not always return the same error code: it's
            # something of a crapshoot whether it's broken pipe or
            # connection reset by peer.
            if (not use_except) or (why[0] not in (EPIPE, ECONNRESET)):
                raise
            result = ""
    finally:
        sock.close()
    exitcode = child.exitcode()
    return (exitcode, result)


class ForkWaitTest(unittest.TestCase):
    
    def test_forkwait(self):
        self.assertEqual(forkwait_test(dummy_fn, dummy_fn), 0)
        self.assertEqual(forkwait_test(dummy_fn, bad_fn), 254)
        self.assertEqual(forkwait_test(dummy_fn, None), 254)
        self.assertRaises(IOError, forkwait_test, bad_fn, None)
        self.assertRaises(IOError, forkwait_test, None, None)


class SocketPairTest(unittest.TestCase):
    
    def test_socketpair(self):
        self.assertEqual(socketpair_test(socket_fn), (0, test_byte))
        self.assertEqual(socketpair_test(bad_socket_fn, True), (249, ""))
        self.assertEqual(socketpair_test(None, True), (249, ""))


if __name__ == '__main__':
    unittest.main()

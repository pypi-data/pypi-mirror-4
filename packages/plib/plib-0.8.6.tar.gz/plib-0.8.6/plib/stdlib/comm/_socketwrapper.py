#!/usr/bin/env python
"""
Module SOCKETWRAPPER -- Socket Pair Wrapper Function
Sub-Package STDLIB.COMM of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``socketpair_wrapper`` function, which
provides a portable interface for creating socket pairs to
communicate with child processes and threads.

Note that on Windows the ``multiprocessing`` module is used
for child process support, which is only available in Python
2.6 and later.
"""

import socket


if hasattr(socket, 'socketpair'):
    # We're on a Unix-type system, so no special gymnastics needed
    
    
    def _child(client_sock, daemon_sock, fn, is_process):
        # Child process/thread
        
        # Hack so we can use the same function for both
        # processes and threads (in a child thread we don't
        # want to close the client socket since that will
        # kill it for the parent thread too)
        if is_process:
            try:
                client_sock.close()
            except:
                return 248
        try:
            # The user function is responsible for closing the socket
            # (this includes if an exception happens--the except
            # clause below is only meant to catch exceptions that
            # the user function doesn't want to define a different
            # return code for)
            retcode = fn(daemon_sock)
            if retcode is None:
                retcode = 0
            return retcode
        except:
            return 249
    
    
    def socketpair_wrapper(fn, Wrapper):
        is_process = 'Process' in Wrapper.__name__
        client_sock, daemon_sock = socket.socketpair()
        child = Wrapper(_child, client_sock, daemon_sock, fn,
            is_process)
        child.start()
        # Same hack as above, don't want to close the daemon socket
        # in a thread since that kills it for the child too
        if is_process:
            daemon_sock.close()
        # The caller is responsible for closing the client socket
        return (client_sock, child)


else:
    # We're on Windows, so we have to emulate socketpair
    
    
    def _child(port, fn):
        # Child process/thread, must connect with parent to establish
        # the socket pair
        try:
            daemon_sock = socket.socket()
        except:
            return 246
        try:
            daemon_sock.connect(('localhost', port))
        except:
            return 247
        try:
            # The user function is responsible for closing the socket
            # (this includes if an exception happens--the except
            # clause below is only meant to catch exceptions that
            # the user function doesn't want to define a different
            # return code for)
            retcode = fn(daemon_sock)
            if retcode is None:
                retcode = 0
            return retcode
        except:
            return 249
    
    
    def socketpair_wrapper(fn, Wrapper):
        listensock = socket.socket()
        listensock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listensock.bind( ('localhost', 0) )
        iface, ephport = listensock.getsockname()
        listensock.listen(1)
        child = Wrapper(_child, ephport, fn)
        child.start()
        client_sock, addr = listensock.accept()
        listensock.close()
        # The caller is responsible for closing the client socket
        return (client_sock, child)

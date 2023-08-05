#!/usr/bin/env python
"""
Module WAITWRAPPER -- Child Waiting Wrapper Function
Sub-Package STDLIB.COMM of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``wait_wrapper`` function, which
starts a child process or thread and then waits until the child
has started before continuing.

Note that on Windows the ``multiprocessing`` module is used
for child process support, which is only available in Python
2.6 and later.
"""

from os import name as os_name

server_ok = "1"

if os_name == "posix":
    # We're on a Unix-type system and can use os.pipe safely
    
    import os
    
    
    def _child(rfd, wfd, start_fn, run_fn, is_process):
        # Child process/thread; note that the exit codes we return
        # are out of the range of possible errno values, to ensure
        # that we can tell what error happened
        try:
            try:
                # Hack so we can use the same function for both
                # processes and threads (in a child thread we don't
                # want to close this file descriptor since that will
                # kill it for the parent thread too)
                if is_process:
                    os.close(rfd)
                start_fn()
                os.write(wfd, server_ok)
            except:
                return 253
        finally:
            try:
                # We can close this file descriptor since we're done
                # with it
                os.close(wfd)
            except:
                pass
        try:
            retcode = run_fn()
            if retcode is None:
                retcode = 0
            return retcode
        except:
            return 254
    
    
    def wait_wrapper(start_fn, run_fn, Wrapper):
        is_process = 'Process' in Wrapper.__name__
        rfd, wfd = os.pipe()
        child = Wrapper(_child, rfd, wfd, start_fn, run_fn,
            is_process)
        child.start()
        # Same hack as above, don't want to close this file descriptor
        # in a thread since that kills it for the child too
        if is_process:
            os.close(wfd)
        try:
            ok = os.read(rfd, len(server_ok))
            if ok != server_ok:
                raise IOError, "fork_wait aborted!"
        finally:
            # We can close this file descriptor since we're done
            # with it
            os.close(rfd)
        return child


else:
    # We're on Windows so os.pipe won't work as is; we could use the
    # multiprocessing module's Pipe object (which allows pipes to be
    # inherited by child processes), but it doesn't seem to work with
    # the fork_wait logic we're using (closing one end of the pipe
    # seems to guarantee EOFError on the other end even if data was
    # written before the close and therefore should be readable--???),
    # so we use socketpair_wrapper instead, which is known to work
    
    from functools import partial
    
    from ._socketwrapper import socketpair_wrapper
    
    
    def _child(start_fn, run_fn, sock):
        # We'll form a partial so the function sent to
        # socketpair_wrapper only takes the sock argument (this
        # works as long as we use functools.partial directly,
        # to ensure that it's picklable by multiprocessing)
        try:
            try:
                start_fn()
                sock.sendall(server_ok)
            except:
                return 253
        finally:
            try:
                # We can close this socket here since we're done with it
                sock.close()
            except:
                pass
        try:
            retcode = run_fn()
            if retcode is None:
                retcode = 0
            return retcode
        except:
            return 254
    
    
    def wait_wrapper(start_fn, run_fn, Wrapper):
        sock, child = socketpair_wrapper(
            partial(_child, start_fn, run_fn),
            Wrapper)
        try:
            ok = sock.recv(len(server_ok))
            if ok != server_ok:
                raise IOError, "fork_wait aborted!"
        finally:
            # We can close this socket here since we're done with it
            sock.close()
        return child

#!/usr/bin/env python
"""
Module SIGTOOLS -- PLIB Signal Handling Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains utilities for use in handling
signals.
"""

import os
import atexit
import signal
from functools import partial

from plib.stdlib.coll import fifo


# First the os-specific code

if os.name == 'posix':
    # We're on a Unix-type system and can use os.pipe with select
    
    from plib.stdlib.fdtools import set_nonblocking
    
    
    _read_fd = None
    _write_fd = None
    
    
    def _cleanup_pipe(*fds):
        for fd in fds:
            os.close(fd)
    
    
    def _setup_pipe():
        global _read_fd, _write_fd
        if _read_fd is None:
            _read_fd, _write_fd = os.pipe()
            for fd in (_read_fd, _write_fd):
                set_nonblocking(fd)
            signal.set_wakeup_fd(_write_fd)
            atexit.register(partial(_cleanup_pipe, _read_fd, _write_fd))
    
    
    def selfpipe_fd():
        _setup_pipe()
        return _read_fd
    
    
    def _flush_pipe():
        # The pipe will contain all \x00 bytes, so there's no
        # use retaining them; we just need to allow for either
        # an os.error or a zero-byte read signaling that the
        # pipe is empty
        while True:
            try:
                b = os.read(_read_fd, 1)
            except os.error:
                break
            else:
                if not b:
                    break
    
    
    def send_signal(sig):
        os.kill(os.getpid(), sig)


else:
    # We're on Windows and have to use an (emulated) socketpair to
    # emulate a select-able pipe
    
    from plib.stdlib.comm._threadwrapper import ThreadWrapper
    from plib.stdlib.comm._socketwrapper import socketpair_wrapper
    
    
    _read_sock = None
    _write_sock = None
    
    
    def _cleanup_pipe(*socks):
        for sock in socks:
            sock.close()
    
    
    def _pipe(wsock):
        global _write_sock
        wsock.setblocking(0)
        _write_sock = wsock
    
    
    def _setup_pipe():
        global _read_sock
        if _read_sock is None:
            _read_sock, child = socketpair_wrapper(
                _pipe, ThreadWrapper)
            _read_sock.setblocking(0)
            child.wait()  # _write_sock will be filled in when this returns
            signal.set_wakeup_fd(_write_sock.fileno())
            atexit.register(partial(_cleanup_pipe, _read_sock, _write_sock))
    
    
    def selfpipe_fd():
        _setup_pipe()
        return _read_sock.fileno()
    
    
    def _flush_pipe():
        # The pipe will contain all \x00 bytes, so there's no
        # use retaining them; we just need to allow for either
        # a socket.error or a zero-byte read signaling that the
        # pipe is empty
        while True:
            try:
                b = _read_sock.recv(1)
            except socket.error:
                break
            else:
                if not b:
                    break
    
    
    def send_signal(sig):
        _sigs_received.append(sig)
        try:
            _write_sock.send('\x00')
        except socket.error:
            # If the pipe is already full we are fine anyway
            pass


# Now the common code

_reset_signals = set()

_sigs_received = fifo()


def _sighandler(sig, frame):
    _sigs_received.append(sig)
    if sig in _reset_signals:
        # These signals have to have the handler reset every time
        signal.signal(sig, _sighandler)


_old_handlers = {}


def _setup_sig(sig, reset=False):
    if sig not in _old_handlers:
        _setup_pipe()
        _old_handlers[sig] = signal.signal(sig, _sighandler)
        if reset:
            _reset_signals.add(sig)


def track_signal(sig, reset=False):
    _setup_sig(sig, reset)
    return _old_handlers[sig]


def track_signals(*sigs):
    for sig in sigs:
        _setup_sig(sig)
    return tuple(_old_handlers[sig] for sig in sigs)


def _cleanup_sig(sig):
    if sig in _old_handlers:
        signal.signal(sig, _old_handlers[sig])
        del _old_handlers[sig]
        if sig in _reset_signals:
            _reset_signals.discard(sig)


def untrack_signal(sig):
    _cleanup_sig(sig)


def untrack_signals(*sigs):
    for sig in sigs:
        _cleanup_sig(sig)


def signals_received():
    # Flush the pipe first, then check signals received, to avoid
    # a race if a signal arrives after exiting the while loop below
    _flush_pipe()
    while _sigs_received:
        yield _sigs_received.next()

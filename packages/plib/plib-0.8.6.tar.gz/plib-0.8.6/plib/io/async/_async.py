#!/usr/bin/env python
"""
Module ASYNC -- Asynchronous I/O Utilities
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the base class for asynchronous I/O
functionality. The idea is the same as the asyncore module
in the Python standard library, but the core is abstracted
out so it can be used with various I/O types, not just
network sockets.

There is also a modified asynchronous loop function that
allows a callback on every iteration, which is useful if a
separate event loop needs to be kept running in parallel
with the async loop (for example, a GUI event loop).
"""

import asyncore
import select
import time
from errno import EBADF

_use_poll = True


# Need an accessor since this module gets imported into the
# package using from import *

def use_poll(flag):
    global _use_poll
    _use_poll = flag


# Monkeypatch asyncore to change the implementation of
# the read/write functions so that we pass all exceptions
# through handle_error (which re-raises them by default
# after closing the channel, so there's no need to give
# ExitNow any special treatment), and to enforce consistent
# semantics (since the semantics of asyncore's underlying
# polling loop functions have changed several times through
# Python versions, not always in ways beneficial to our
# approach here.)

# Note that for our code to work with code that uses asyncore
# but not our I/O classes, we have to check the type of each
# async object and only run our version if it's one of ours


_read = asyncore.read
def read(obj):
    if isinstance(obj, AsyncBase):
        try:
            obj.handle_read_event()
        except:
            obj.handle_error()
    else:
        _read(obj)
asyncore.read = read


_write = asyncore.write
def write(obj):
    if isinstance(obj, AsyncBase):
        try:
            obj.handle_write_event()
        except:
            obj.handle_error()
    else:
        _write(obj)
asyncore.write = write


_exc = asyncore._exception
def _exception(obj):
    if isinstance(obj, AsyncBase):
        try:
            obj.handle_expt_event()
        except:
            obj.handle_error()
    else:
        _exc(obj)
asyncore._exception = _exception


_readwrite = asyncore.readwrite
def readwrite(obj, flags):
    if isinstance(obj, AsyncBase):
        try:
            if flags & (select.POLLIN | select.POLLPRI):
                obj.handle_read_event()
            if flags & select.POLLOUT:
                obj.handle_write_event()
            if flags & (select.POLLERR | select.POLLHUP | select.POLLNVAL):
                obj.handle_expt_event()
        except:
            obj.handle_error()
    else:
        _readwrite(obj, flags)
asyncore.readwrite = readwrite


def loop(timeout=30.0, map=None, callback=None, count=None):
    """Basic asynchronous polling loop.
    
    This async looping function allows a callback function
    to run on each loop iteration; if the callback returns
    ``False`` (the specific object, not just a value that tests
    false), it breaks out of the loop.
    """
    
    if map is None:
        map = asyncore.socket_map
    
    if _use_poll and hasattr(select, 'poll'):
        poll_fun = asyncore.poll2
    else:
        # Need to compensate for the fact that if select breaks
        # on a bad file descriptor, it can't tell us *which* one
        # it was, so we have tell *each* object to check to see
        # if there might be an error (poll just sets the POLLHUP
        # flag for that specific fd so this hack isn't needed)
        def poll_fun(timeout, map):
            try:
                asyncore.poll(timeout, map)
            except select.error, err:
                if err[0] != EBADF:
                    raise
                else:
                    for fd, obj in map.iteritems():
                        _exception(obj)
    
    if count is None:
        if callback is None:
            while map:
                poll_fun(timeout, map)
        else:
            while map and (callback() is not False):
                poll_fun(timeout, map)
    
    else:
        if callback is None:
            while map and count > 0:
                poll_fun(timeout, map)
                count = count - 1
        else:
            while map and (count > 0) and (callback() is not False):
                poll_fun(timeout, map)
                count = count - 1


class AsyncBase(object):
    """Base class for async communication channel.
    
    Base class that abstracts out the core functionality
    for asynchronous I/O. Can be used to wrap any object
    that has a Unix file descriptor; the ``set_fileobj``
    method must be called with the object to be wrapped.
    Note that this class does *not* set file descriptors
    to non-blocking mode; that can't be reliably done
    here because there are too many different types of
    descriptors. Thus, users of this class must first set
    their file descriptors to non-blocking mode before
    calling the ``set_fileobj`` method.
    
    This class also allows a callback function on
    each iteration of the polling loop. This allows other
    processing to be done while waiting for I/O (one
    common use case would be keeping a GUI event loop
    running concurrently with the network polling loop).
    Note that if a callback is used this way, the
    ``poll_timeout`` field should be set to a reasonably
    short float value (e.g., 1.0--the value is in seconds).
    The default for this field is ``None`` since we use
    the self-pipe trick for signal notification, so there
    is normally no need to time out.
    """
    
    debug = False
    poll_timeout = None
    
    def __init__(self, map=None):
        if map is None:
            self._map = asyncore.socket_map
        else:
            self._map = map
        self._fileno = None
    
    def __repr__(self):
        status = [self.__class__.__module__ + "." + self.__class__.__name__]
        self.repr_status(status)
        return '<%s at %#x>' % (' '.join(status), id(self))
    
    def repr_status(self, status):
        pass # derived classes can add more stuff to repr here
    
    def fileno(self):
        return self._fileno # so we look file-like
    
    def set_fileobj(self, obj, map=None):
        self._fileno = obj.fileno()
        self.add_channel(map)
    
    def add_channel(self, map=None):
        if map is None:
            map = self._map
        #if map.has_key(self._fileno):
        #    raise RuntimeError("%r tried to add itself to the map twice!" % self)
        map[self._fileno] = self
    
    def del_channel(self, map=None):
        fd = self._fileno
        if fd is not None:
            if map is None:
                map = self._map
            if map.has_key(fd):
                del map[fd]
            self._fileno = None
    
    def close(self):
        self.del_channel()
        self.handle_close()
    
    def readable(self):
        return True
    
    def writable(self):
        return True
    
    def handle_read_event(self):
        self.handle_read()
    
    def handle_write_event(self):
        self.handle_write()
    
    def handle_expt_event(self):
        self.handle_expt()
    
    def handle_error(self):
        """More Pythonic way of handling errors.
        """
        self.close()
        raise
    
    def handle_read(self):
        """Derived classes must implement this method to read data.
        """
        raise NotImplementedError
    
    def handle_write(self):
        """Derived classes must implement this method to write data.
        """
        raise NotImplementedError
    
    def handle_expt(self):
        """Check to see if we have an error.
        
        Called when select/poll indicates that there might be an
        error on our file descriptor.
        """
        self.check_error()
    
    def check_error(self):
        """Placeholder for derived classes.
        """
        pass
    
    def handle_close(self):
        self.on_close()
    
    def on_close(self):
        """Placeholder for derived classes.
        """
        pass
    
    def do_loop(self, callback=None):
        """Basic async polling loop.
        
        Convenience looping method that allows a callback function
        to be called on each iteration of the polling loop. Note that
        we allow the callback to break us out of the loop by returning
        ``False`` (not just any false value, but the specific object
        ``False``).
        
        Note that when there are multiple async channels (e.g., in a
        socket server handling multiple connections), only one object
        should call this function (since only one async loop can run
        at a time); normally that will be the "server" object (each
        request handler then just gets added to the map for the server's
        polling loop).
        """
        loop(self.poll_timeout, self._map, callback)

#!/usr/bin/env python
"""
Module THREADWRAPPER -- Child Thread Wrapper Object
Sub-Package STDLIB.COMM of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

This module contains the ``ThreadWrapper`` class, which provides
a portable interface to child threads and their exit status.
This class is used by the specialized threading functions in this
library.
"""

import threading

from ._childwrapper import ChildWrapper


class ChildThread(threading.Thread):
    # Fortunately we don't have to go through the same gymnastics
    # as for child processes (see the _processwrapper module)
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        # We save this info so run can see it below (the base class
        # stores them as private vars)
        self._target = target
        self._args = args
        self._kwargs = kwargs
        threading.Thread.__init__(self, group=group, name=name,
            verbose=verbose)
    
    def run(self):
        # And now we need to actually return the exit code
        # (at least this part is easily implemented...)
        if self._target:
            self.exitcode = self._target(*self._args, **self._kwargs)


class ThreadWrapper(ChildWrapper):
    
    thread_class = ChildThread
    
    thread = None
    
    def start(self):
        if self.thread is None:
            self.thread = self.thread_class(
                target=self._target, args=self._args, kwargs=self._kwargs)
            self.thread.setDaemon(self.shutdown_with_parent)
            self.thread.start()
        else:
            raise RuntimeError("Thread already started.")
    
    def stop(self):
        # No way to stop a thread by default; this method can be overridden
        # to allow interaction with the thread via events or other means (in
        # such cases the thread_class class field can also be overridden to
        # use a subclass of ChildThread)
        pass
    
    def check(self):
        if self.thread is None:
            return True
        if not self.thread.is_alive():
            self._exitcode = self.thread.exitcode
            self.thread = None
            return True
        return False
    
    def wait(self):
        self.thread.join()
        self._exitcode = self.thread.exitcode
        self.thread = None

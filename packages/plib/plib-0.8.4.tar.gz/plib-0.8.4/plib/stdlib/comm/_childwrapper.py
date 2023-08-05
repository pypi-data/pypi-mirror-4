#!/usr/bin/env python
"""
Module CHILDWRAPPER -- Base Child Process/Thread Wrapper Object
Sub-Package STDLIB.COMM of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

This module contains the ``ChildWrapper`` class, which provides
a portable abstract interface to child processes and threads
and their exit status.
"""


class ChildWrapper(object):
    """Base abstract interface for handling child processes/threads.
    
    The ``shutdown_with_parent`` flag determines whether the
    child should be shut down when its parent finishes, or
    whether it should continue independently. The former is
    typical for, say, request handlers spawned by servers;
    the latter is more useful for, say, forking the server
    process itself. The default is ``False``.
    """
    
    shutdown_with_parent = False
    
    _exitcode = None
    
    def __init__(self, target, *args, **kwargs):
        self._target = target
        self._args = args
        self._kwargs = kwargs
    
    def start(self):
        """Start the child process/thread.
        
        This method must only start the child once; if it is
        called multiple times, the second and subsequent calls
        must do nothing to the process. It is undefined whether
        multiple calls to this method will raise an exception
        (the implementations below raise RuntimeError).
        """
        raise NotImplementedError
    
    def stop(self):
        """Stop the child process/thread.
        
        This method must not cause an error if called multiple times.
        Thus, it must be able to tell if the process has already been
        stopped, and not try to stop it again.
        """
        raise NotImplementedError
    
    def check(self):
        """Check whether the child process/thread has stopped.
        
        If this function returns true, ``exitcode`` can be called to
        get the child's exit code.
        """
        raise NotImplementedError
    
    def wait(self):
        """Wait for the child process/thread to exit and get its exit code.
        
        After this method is called, ``self._exitcode`` must contain
        the exit code of the process.
        
        This method must not cause an error if called multiple times.
        Thus, it must be able to tell if the process has already
        exited, and not try to wait for it again.
        """
        raise NotImplementedError
    
    def exitcode(self):
        """Return the child process/thread exit code.
        
        Note that this method does not force the child to stop, so
        it could hang indefinitely unless ``stop`` is called before
        this method (or unless you have some other way of ensuring
        that the child is stopped first).
        """
        self.wait()
        return self._exitcode
    
    def end(self):
        """Ensure that the child is done.
        
        The exit code can be retrieved by calling ``exitcode``
        after this method returns.
        """
        self.stop()
        self.wait()

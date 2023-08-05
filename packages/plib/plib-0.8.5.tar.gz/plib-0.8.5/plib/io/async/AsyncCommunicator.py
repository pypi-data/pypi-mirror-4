#!/usr/bin/env python
"""
Module AsyncCommunicator
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous AsyncCommunicator class.
"""


class AsyncCommunicator(object):
    """Communicator mixin class for async I/O.
    
    Adds checking of the ``done`` flag to the ``do_loop`` method,
    so we break out of the loop if the flag is set. Note that
    calling the ``do_loop`` method implies that this object is
    the "master" async I/O object; it should *not* be called,
    for example, in request handlers.
    """
    
    def do_loop(self, callback=None):
        """Assume we're controlling the loop, so check ``done`` to exit.
        """
        if callback is not None:
            def f():
                if (callback() is False) or self.done:
                    return False
        else:
           def f():
               if self.done:
                    return False
        super(AsyncCommunicator, self).do_loop(f)
    
    def run_loop(self, callback=None):
        self.do_loop(callback)

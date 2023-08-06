#!/usr/bin/env python
"""
Module ChildWrapperMixin
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``ChildWrapperMixin`` class, which
implements common functionality for servers conforming to
the PLIB I/O API that create child processes or threads
to handle requests.
"""

from functools import partial


def _child(error_fn, child_fn):
    # Child process/thread function
    try:
        child_fn()
        return 0
    except:
        try:
            error_fn()
        except:
            pass
        return 1


class ChildWrapperMixin(object):
    """Mixin class for PLIB servers to handle child processes/threads.
    
    Subclasses must fill in the ``wrapper_class`` field with a
    ``ChildWrapper`` subclass which will be used to instantiate each
    request handler process/thread.
    """
    
    wrapper_class = None
    
    def server_start(self):
        super(ChildWrapperMixin, self).server_start()
        # Make sure our request handlers shut down when we do
        self.wrapper_class.shutdown_with_parent = True
    
    def _errorhandler(self, request):
        # Internal function returns an error handler that closes request
        try:
            request.close()
        except:
            pass
        self.handle_error()
    
    def _new_child(self, handler, conn, addr):
        return self.wrapper_class(_child,
            partial(self._errorhandler, conn),
            partial(self.handler, conn, addr, self))
    
    def start_child(self, handler, conn, addr):
        child = self._new_child(handler, conn, addr)
        child.start()

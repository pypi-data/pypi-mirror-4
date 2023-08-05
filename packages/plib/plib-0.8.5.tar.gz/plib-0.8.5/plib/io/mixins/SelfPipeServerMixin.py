#!/usr/bin/env python
"""
Module SelfPipeServerMixin
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SelfPipeServerMixin`` class,
which provides "drop-in" usage of ``SelfPipe`` for
servers that conform to the PLIB I/O server API. The
``SocketServer`` class in ``plib.io.async`` uses
this class to implement the self-pipe trick.
"""

from functools import partial

from .SelfPipe import SelfPipe


class SelfPipeServerMixin(object):
    """Implements the self-pipe trick for PLIB servers.
    
    The ``pipe_class`` field stores the class that will be instantiated
    to create the pipe (an example is the async socket server, as
    noted above).
    """
    
    pipe_class = SelfPipe
    
    pipe = None
    
    def signal_callback(self, sig):
        # Override to process signals received when the pipe is triggered
        pass
    
    def server_start(self):
        super(SelfPipeServerMixin, self).server_start()
        self.pipe = self.pipe_class(self.signal_callback)

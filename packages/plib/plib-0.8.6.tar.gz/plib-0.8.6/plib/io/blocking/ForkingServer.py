#!/usr/bin/env python
"""
Module ForkingServer
Sub-Package IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``ForkingServer`` class, which
is a forking version of the blocking I/O socket server.
See the module docstring for the base class, ``SocketServer``,
for more information.
"""

import signal

from plib.stdlib.comm._processwrapper import ProcessWrapper

from plib.io.blocking import SocketServer
from plib.io.mixins import ChildWrapperMixin


class ForkingServer(ChildWrapperMixin, SocketServer):
    """Forking TCP server.
    
    This server forks a new child process for each request
    and instantiates a request handler in the child. Note
    that this server does no tracking of child processes
    once they are forked; on Unix-type systems, it sets its
    SIGCHLD handler to SIG_IGN so that the kernel will reap
    its children once they exit. If actual tracking of the
    child processes is desired, the ``SigChldServerMixin``
    class can be used to add that functionality.
    """
    
    wrapper_class = ProcessWrapper
    
    ignore_sigchld = True
    
    def server_start(self):
        super(ForkingServer, self).server_start()
        # This tells the kernel to reap our zombies for us
        # (note that we include a flag here to allow a derived
        # class, such as one using SigChldServerMixin, to
        # disable this, usually because the derived class
        # sets its own SIGCHLD handler)
        if self.ignore_sigchld and hasattr(signal, 'SIGCHLD'):
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    
    def start_child(self, handler, conn, addr):
        super(ForkingServer, self).start_child(handler, conn, addr)
        conn.close()  # only the child needs it now

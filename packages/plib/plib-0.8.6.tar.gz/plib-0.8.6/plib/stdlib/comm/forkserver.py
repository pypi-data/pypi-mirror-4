#!/usr/bin/env python
"""
Module FORKSERVER -- Server Forking Function
Sub-Package STDLIB.COMM of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the fork_server function, which
forks a subprocess that starts a server of the given class,
and then waits until the server has started before continuing.

Function parameters:

- ``server_class``: either a class object with a ``serve_forever``
  method, or a tuple (<module_name>, <class_name>) pointing to such
  an (importable) object

- ``server_addr``: an appropriate address for the type of server
  (e.g., (<hostname>, <port>) for TCP servers); if not present, it
  will be assumed that instantiating the server class is sufficient
  to bind the server to the appropriate address

- ``handler_class``: a class object which will be used as the request
  handler; if not present, it will be assumed that the server class
  contains the necessary information (which is usually the case)

Note that on Windows the ``multiprocessing`` module is used,
which is only available in Python 2.6 and later.
"""

from .forkwait import fork_wait
from ._serverproxy import ServerProxy


def fork_server(server_class, server_addr=None, handler_class=None):
    proxy = ServerProxy(server_class, server_addr, handler_class)
    return fork_wait(proxy.start_server, proxy.run_server)

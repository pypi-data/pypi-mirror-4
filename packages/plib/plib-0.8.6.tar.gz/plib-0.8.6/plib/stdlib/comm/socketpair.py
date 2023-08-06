#!/usr/bin/env python
"""
Module SOCKETPAIR -- Socket Pair Forking Function
Sub-Package STDLIB.COMM of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the fork_socketpair function, which
forks a subprocess that communicates with its parent via
a socket pair.

Note that on Windows the ``multiprocessing`` module is used,
which is only available in Python 2.6 and later.
"""

from ._processwrapper import ProcessWrapper
from ._socketwrapper import socketpair_wrapper


def fork_socketpair(fn):
    return socketpair_wrapper(fn, ProcessWrapper)

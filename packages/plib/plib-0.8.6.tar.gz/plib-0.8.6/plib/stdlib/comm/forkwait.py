#!/usr/bin/env python
"""
Module FORKWAIT -- Specialized Forking Function
Sub-Package STDLIB.COMM of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``fork_wait`` function, which
forks a subprocess and then waits until the subprocess
has started before continuing.

Note that on Windows the ``multiprocessing`` module is used,
which is only available in Python 2.6 and later.
"""

from ._processwrapper import ProcessWrapper
from ._waitwrapper import wait_wrapper


def fork_wait(start_fn, run_fn):
    return wait_wrapper(start_fn, run_fn, ProcessWrapper)

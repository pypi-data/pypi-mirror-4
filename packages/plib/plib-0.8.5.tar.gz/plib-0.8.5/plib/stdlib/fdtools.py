#!/usr/bin/env python
"""
Module FDTOOLS -- PLIB File Descriptor Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains utilities for working with file
descriptors.

Utility functions currently provided:

set_nonblocking -- make a file descriptor non-blocking.
"""

from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK


def set_nonblocking(fd):
    flags = fcntl(fd, F_GETFL)
    fcntl(fd, F_SETFL, flags | O_NONBLOCK)

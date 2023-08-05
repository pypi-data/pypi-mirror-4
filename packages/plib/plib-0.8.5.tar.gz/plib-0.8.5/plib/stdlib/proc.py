#!/usr/bin/env python
"""
Module PROC -- Process-Related Utilities
Sub-Package STDLIB of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module is for useful process-related functions. Currently
the only function implemented is ``process_output``, which
runs an external process and returns its output as a string.
"""

from subprocess import Popen, PIPE
from shlex import split


def process_output(cmdline):
    s = ""
    p = Popen(split(cmdline), stdout=PIPE).stdout
    try:
        s = p.read()
    finally:
        p.close()
    return s

#!/usr/bin/env python
"""
Module SYSTOOLS -- PLIB System Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains information about the system on which
PLIB and the Python interpreter are running, and utilities
for working with that information.

variables pythonpath, plibpath, binpath, sharepath --
    contain pathnames to root python directory, plib directory,
    third-party binary directory, and third-party shared data directory
    (the latter two are where plib's scripts and example programs will
    have been installed)
"""

from ._paths import *

#!/usr/bin/env python
"""
Module SerialBase
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous SerialBase class.
"""

from plib.io.serial import SerialData
from plib.io.async import SerialDispatcher


class SerialBase(SerialData, SerialDispatcher):
    """Serial async I/O class with data handling.
    """
    pass

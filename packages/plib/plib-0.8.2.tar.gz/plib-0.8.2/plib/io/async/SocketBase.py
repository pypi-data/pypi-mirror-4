#!/usr/bin/env python
"""
Module SocketBase
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous SocketBase class.
"""

from plib.io.socket import SocketData
from plib.io.async import SocketDispatcher


class SocketBase(SocketData, SocketDispatcher):
    """Base class for socket async I/O.
    
    Socket async I/O class with data handling and defaults
    for events that don't need handlers.
    """
    pass

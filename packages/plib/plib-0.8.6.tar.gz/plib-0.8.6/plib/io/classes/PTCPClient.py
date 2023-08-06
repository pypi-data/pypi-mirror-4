#!/usr/bin/env python
"""
Module PTCPClient
Sub-Package IO.CLASSES of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``PTCPClient`` class. This is a
blocking socket I/O client using the ``PClientBase``
interface.
"""

from plib.io.blocking import SocketClient
from plib.io.classes import PClientBase


class PTCPClient(PClientBase, SocketClient):
    """Blocking TCP client class.
    
    Connects with TCP server, writes data, and stores the
    result. See the ``PClientBase`` docstring for more
    information.
    """
    pass

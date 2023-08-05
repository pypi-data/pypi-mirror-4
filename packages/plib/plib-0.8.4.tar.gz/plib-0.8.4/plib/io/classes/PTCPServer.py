#!/usr/bin/env python
"""
Module PTCPServer
Sub-Package IO.CLASSES of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``PTCPServer`` class. This is a forking
TCP server that includes the general signal handling and
logging facilities of ``PServerBase``.
"""

from plib.io.blocking import BaseRequestHandler, SocketServer

from PServerBase import PServerBase


class PTCPServer(PServerBase, SocketServer):
    """Generic forking server class with enhanced common functionality.
    
    This generic forking server implements signal handling for controlled
    termination, and log file functionality. The intent is to trap any
    signal that might be used to indicate general 'program shutdown' as
    opposed to some specific error condition (i.e., any signal where it
    can be assumed that controlled shutdown of the Python interpreter
    is possible).
    """
    
    handler_class = BaseRequestHandler

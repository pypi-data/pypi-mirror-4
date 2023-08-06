#!/usr/bin/env python
"""
Module SerialTelnet
Sub-Package IO.CLASSES of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the SerialTelnet class. This is a
telnet client that can communicate over a serial port;
it uses the ``SerialPseudoSocket`` class from this
sub-package to add serial device I/O functionality.
"""

import telnetlib

from plib.io.classes import SerialPseudoSocket


class SerialTelnet(telnetlib.Telnet):
    """Telnet client that can use a serial port or a socket.
    
    Use the ``openserial`` method to open a serial device,
    and ``open`` to open a socket. Does not allow any
    parameters to the constructor (so you have to explicitly
    call the appropriate opening method).
    """
    
    def __init__(self):
        telnetlib.Telnet.__init__(self) # don't allow any constructor params
    
    def openserial(self, devid):
        self.sock = SerialPseudoSocket(devid, blocking_mode=True)

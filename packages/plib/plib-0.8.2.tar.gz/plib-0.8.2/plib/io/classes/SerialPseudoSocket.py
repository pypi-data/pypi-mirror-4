#!/usr/bin/env python
"""
Module SerialPseudoSocket
Sub-Package IO.CLASSES of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the SerialPseudoSocket class. This
is a specialized serial device class that provides a
(minimal) socket-like interface, so that it can be used
in place of a socket for applications that expect one.
An example of this usage is the SerialTelnet class in
this sub-package, which uses this class as a simple
"drop-in" replacement for the Python standard library
``socket`` class to implement a telnet client that can
communicate over a serial port.
"""

from plib.io.serial import Serial


class SerialPseudoSocket(Serial):
    """A wrapper to make a serial port look minimally like a socket.
    
    Make a serial port look like a socket (at least enough so
    to fool most minimal socket-using applications).
    """
    
    def recv(self, bufsize):
        return self.read(bufsize)
    
    def send(self, data):
        return self.write(data)
    
    def sendall(self, data):
        while data:
            sent = self.write(data)
            data = data[sent:]

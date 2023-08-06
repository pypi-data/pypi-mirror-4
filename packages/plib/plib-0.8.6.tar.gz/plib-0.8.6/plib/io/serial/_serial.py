#!/usr/bin/env python
"""
Module SERIAL -- Serial Port Handling
Sub-Package IO.SERIAL of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains a thin wrapper class around the
``Serial`` class from the pyserial package. The wrapper just
adds some options for using the class that work around
potential quirks in various types of serial devices. Note
that the wrapper class is only implemented for POSIX
systems; on other systems the only class added by this
module is the data overlay class.
"""

import os
import errno

from plib.io.base import BaseData, BaseIO

if os.name != 'posix':
    from serial import Serial

else:
    import fcntl
    import serial # provided by pyserial package
    from serial import SerialException, EIGHTBITS, PARITY_NONE, STOPBITS_ONE
    
    
    class Serial(serial.Serial):
        """
        Thin wrapper class around ``serial.Serial``. Key changes:
        
        - Adds option to go back into blocking mode after the
          port is opened (the open needs to be non-blocking to
          avoid indefinite waits on devices).
        - Eliminates the select call from the read and write
          methods; it isn't needed since this class is intended
          to be mixed in with the ``AsyncBase`` async I/O class,
          which handles the select functionality (see the
          ``async.SerialDispatcher`` module for the implementation
          of this).
        - The ``read`` method may return fewer bytes than the size
          parameter instead of looping until that many bytes are
          read, and it raises an exception on any error except
          ``EAGAIN`` (for which it returns an empty string).
        - The ``write`` method returns the number of bytes written
          instead of looping until it's all written.
        - Because of the above changes to ``read`` and ``write``,
          the timeout parameters have no effect; instead, use the
          ``blocking_mode`` flag to control read and write behavior.
        
        The changes to the read and write methods make this a more
        low-level class; the higher-level classes overlaid on this
        one in the ``async`` and ``blocking`` sub-packages then take
        care of managing whether all desired bytes have been read or
        written, using the common API for all I/O types.
        """
        
        def __init__(self, port=None, baudrate=9600,
            bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE,
            xonxoff=0, rtscts=0, dsrdtr=None, blocking_mode=False):
            
            self.blocking_mode = blocking_mode
            # Timeouts are None since they're not used here
            serial.Serial.__init__(self, port, baudrate, bytesize,
                parity, stopbits,
                None, xonxoff, rtscts, None, dsrdtr)
        
        def open(self):
            if self._port is None:
                raise SerialException(
                    "Port must be configured before it can be used.")
            self.fd = None
            try:
                self.fd = os.open(self.portstr,
                    os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)
            except Exception, msg:
                self.fd = None
                raise SerialException("could not open port %s: %s" %
                    (self._port, msg))
            
            if self.blocking_mode:
                # Make sure we don't clobber any other flags
                flags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
                flags &= ~os.O_NONBLOCK
                fcntl.fcntl(self.fd, fcntl.F_SETFL, flags)
            
            try:
                self._reconfigurePort()
            except:
                os.close(self.fd)
                self.fd = None
            else:
                self._isOpen = True
        
        def read(self, size=1):
            if self.fd is None:
                raise portNotOpenError
            try:
                data = os.read(self.fd, size)
                return data
            except OSError, err:
                if err.errno != errno.EAGAIN:
                    raise
                return ""
        
        def write(self, data):
            if self.fd is None:
                raise portNotOpenError
            if not isinstance(data, str):
                raise TypeError('expected str, got %s' % type(data))
            try:
                n = os.write(self.fd, data)
                return n
            except OSError, err:
                if err.errno != errno.EAGAIN:
                    raise
                return 0


# Now the base I/O management class, using the above to talk to
# the serial port

class SerialIOBase(BaseIO):
    """
    Base class for serial I/O -- no frills, just reads
    and writes the serial device file. The ``blocking_mode``
    flag controls whether the underlying serial object will
    use blocking or non-blocking I/O.
    """
    
    blocking_mode = False
    
    closed = True
    
    def __init__(self, devid=None):
        if devid is not None:
            self.create_port(devid)
        else:
            self.port = None
    
    def create_port(self, devid):
        self.set_port(Serial(devid, blocking_mode=self.blocking_mode))
    
    def set_port(self, port):
        self.port = port
        self.closed = False
    
    # BaseIO method implementations
    
    def dataread(self, bufsize):
        return self.port.read(self.bufsize)
    
    def datawrite(self, data):
        return self.port.write(self.write_data)
    
    def close(self):
        if self.port is not None:
            self.port.close()
            self.port = None
            self.closed = True


class SerialData(BaseData):
    """Basic data handling for serial I/O.
    """
    
    bufsize = 1

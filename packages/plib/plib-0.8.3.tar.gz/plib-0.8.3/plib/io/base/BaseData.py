#!/usr/bin/env python
"""
Module BaseData
Sub-Package IO of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``BaseData`` class, a base class that
implements common baseline data handling functionality for all
I/O modes (serial vs. socket, blocking/synchronous vs.
non-blocking/asynchronous, etc.). This class assumes that a
``BaseIO`` subclass is earlier in its MRO, implementing the
``dataread`` and ``datawrite`` methods with their defined
semantics.
"""


class BaseData(object):
    """Base class for data handling.
    
    This class is not intended for direct use by user code, but
    provides a single common baseline for the various I/O types,
    including the base implementation of the core methods.
    
    The key limitation of this base data handling mechanism is
    that it has no way to detect that an incoming "message" is
    complete except by detecting a closed channel (which is
    assumed whenever the number of bytes read is less than the
    number of bytes requested). This detection mechanism usually
    works only for a single round-trip data exchange (i.e., one
    read and one write). More sophisticated data handling is
    provided by the classes in the ``plib.io.data``
    sub-package.
    
    Note also that the ``auto_close`` flag should only be left
    ``True`` if it is desired that the entire channel be closed
    whenever a read of zero bytes is detected, which indicates
    that the other endpoint of the socket has called either ``close``
    or ``shutdown``. For read/write handling strategies that use
    the socket ``shutdown`` method to signal that a client has
    finished sending but can still receive (e.g., see the
    ``ShutdownReadWrite`` class), the ``auto_close`` flag must
    be set to ``False`` for the strategy to work properly.
    
    Key data handling methods (the "communicator" classes assume
    that these methods are present with the semantics described
    below--see the ``BaseCommunicator`` docstring):
    
    ** Read Methods **
    
    - ``handle_read``: read data from the channel, store it in
      ``self.read_data``, and determine whether the current read
      cycle is complete. If it is determined that the current
      read cycle is complete, this method ensures that
      ``read_complete`` will return true.
    
    - ``read_complete``: return true if the current read cycle
      is complete. The communicator classes use this method to
      determine when it is safe to switch to write mode.
    
    - ``clear_read``: clear all previously read data, and set up
      for reading more data. This method must only be called if
      ``read_complete`` returns true; after this method returns,
      ``read_complete`` will return false.
    
    ** Write Methods **
    
    - ``start``: set up data for writing. Data can only be started
      one string at a time; user code that needs to write multiple
      strings of data must call this method once for each such
      string, and each subsequent call must not be made until the
      write cycle started by the previous call has completed (see
      ``clear_write`` below).
    
    - ``handle_write``: write data to the channel, and determine
      whether the current write cycle is complete. If it is
      determined that the current write cycle is complete, this
      method ensures that ``write_complete`` will return true.
    
    - ``write_complete``: return true if the current write cycle
      is complete. The communicator classes use this method to
      determine when it is safe to switch to read mode.
    
    - ``clear_write``: clear all data pending for writing, and
      set up for writing more data. This method must only be
      called if ``write_complete`` returns true; after this
      method returns, ``write_complete`` will return false.
      If there is more data that can be written, the ``start``
      method must not be called until after this method returns.
    
    ** State Methods **
    
    - ``channel_closed``: return true if the other end of the
      channel has been closed. This is detected by a read of zero
      bytes. What else happens as a result of this depends on other
      parameters (cf. the discussion of the ``auto_close`` flag
      above).
    """
    
    auto_close = True
    bufsize = None  # must be overridden
    read_data = ""
    read_done = False
    write_data = ""
    shutdown_received = False
    
    def handle_read(self):
        data = self.dataread(self.bufsize)
        if data:
            self.read_data += data
        if len(data) < self.bufsize:
            self.read_done = True
        if (len(data) == 0):
            self.shutdown_received = True
            if self.auto_close:
                self.close()
    
    def read_complete(self):
        return self.read_done
    
    def clear_read(self):
        self.read_data = ""
        self.read_done = False
    
    def start(self, data):
        self.write_data = data
    
    def handle_write(self):
        written = self.datawrite(self.write_data)
        self.write_data = self.write_data[written:]
    
    def write_complete(self):
        return not self.write_data
    
    def clear_write(self):
        self.write_data = ""
    
    def channel_closed(self):
        return self.auto_close and self.shutdown_received

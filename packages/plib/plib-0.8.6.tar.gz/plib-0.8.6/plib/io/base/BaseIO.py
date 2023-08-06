#!/usr/bin/env python
"""
Module BaseIO
Sub-Package IO of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the BaseIO class, which defines a
basic abstract interface for an I/O type. The serial
and socket I/O types subclass this base class. The
``BaseData`` class assumes that a subclass of this class
is earlier in its MRO, so that all ``BaseIO`` methods
are available with their defined semantics.
"""


class BaseIO(object):
    """Base class for I/O types.
    
    This class cannot be instantiated directly, but serves as
    a common subclass defining the interface for all I/O types.
    
    Methods::
    
    - ``dataread``: read up to ``bufsize`` bytes of data and
      return the data read as a ``str``.
    
    - ``datawrite``: write as many bytes of ``data`` (which must
      be a ``str``) as possible, and return the number of bytes
      written.
    
    - ``close``: close the I/O device; after this method is called,
      calls to any other method may produce undefined behavior.
    """
    
    def dataread(self, bufsize):
        """Read up to ``bufsize`` bytes of data, return data read.
        """
        raise NotImplementedError
    
    def datawrite(self, data):
        """Try to write data, return number of bytes written.
        """
        raise NotImplementedError
    
    def close(self):
        """Close the I/O device.
        """
        raise NotImplementedError

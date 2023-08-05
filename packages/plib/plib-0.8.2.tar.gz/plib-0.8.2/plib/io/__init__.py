#!/usr/bin/env python
"""
Sub-Package IO of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package provides a convenient namespace for the
various I/O handling classes included in PLIB. It is
organized into sub-packages itself, with the following
general structure:

- Device Types: Each type of I/O device has its own
  sub-package, which exports the following classes for
  that I/O type: ``BaseClient``, ``BaseServer``, and
  (for socket I/O only) ``BaseRequest``. The device types
  currently supported are serial and socket.

- I/O Modes: Each I/O mode has its own sub-package, which
  exports the following classes for that I/O mode (using
  the device type classes above to handle the grunt work):
  ``SerialClient``, ``SerialServer``, ``SocketClient``,
  ``SocketServer``, and ``BaseRequestHandler``. For the
  async I/O mode only, the following additional classes
  are exported: ``PersistentSerial``, ``PersistentSocket``,
  and ``PersistentRequestHandler``; these support full-duplex,
  persistent asynchronous I/O (meaning multiple reads and
  writes, and reads/writes can be interleaved). There are
  also "mixin" and "base" classes exported so that the same
  functionality can be used with alternate data handling:
  see below for more details. The I/O modes currently
  supported are async and blocking (note that the latter
  does not just mean synchronous: it includes a forking
  TCP server).

- Data Handling: The ``data`` sub-package contains three
  alternate data handling classes, each of which implements
  a particular method for detecting when the end of a given
  "message" in the data stream has been received. The three
  classes are ``ShutdownReadWrite``, ``TerminatorReadWrite``,
  and ``ReadWrite``; see their docstrings for details on how
  they work.

Note that the alternate data handling classes can be mixed
in "by hand" with your desired I/O mode and device type, but
this is usually not necessary. To do the mixin "by hand", you
simply use the "mixin" classes from your desired I/O mode,
along with the "base" class from that I/O mode for your desired
device type, thus::

    from plib.io.async import SocketClientMixin, SocketBase
    from plib.io.data import TerminatorReadWrite
    
    class MySocketClient(SocketClientMixin, TerminatorReadWrite, SocketBase):
        pass

(You could substitute the "mixin" version of any of the other
I/O mode classes above, and you would use ``RequestBase`` or
``SerialBase`` instead of ``SocketBase`` as appropriate.) This
incantation is necessary because the alternate read/write
handling class has to be *after* the client or server class, but
*before* the base device type class, in the MRO for the cooperative
super calls that implement the functionality to work properly.
However, since this pattern is the same each time, it can be
automated, and the ``IOModuleProxy`` class in the ``utils``
module of this sub-package does the automation; see that module's
code and docstring for details on how it works. The upshot is that,
instead of the above, you can simply say::

    from plib.io.async import SocketClientWithTerminator

and the equivalent of the above class derivation will be done "on
the fly" so that the appropriate read/write handling capability is
provided in the class that gets imported. (For the other two data
handling types, the suffix would be 'WithShutdown' or 'WithReadWrite'
instead of 'WithTerminator'.)

In fact, you can even use this same machinery with your own custom
read/write handling class; this is done with the ``get_readwrite_class``
function, which is exposed in each of the I/O mode namespaces. Thus,
you could say::

    from plib.io.async import get_readwrite_class
    
    class MyCustomReadWrite(object):
        [class definition]
    
    MySocketClient = get_readwrite_class('SocketClient', MyCustomReadWrite)

This returns a socket client class with your custom read/write class
spliced into its MRO in the appropriate place. Isn't black magic fun?
"""

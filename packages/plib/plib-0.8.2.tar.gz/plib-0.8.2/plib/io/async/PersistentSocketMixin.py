#!/usr/bin/env python
"""
Module PersistentSocketMixin
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous PersistentSocketMixin class;
this class is factored out from PersistentSocketClient so that alternate
read/write handling can be mixed in.
"""

from plib.io.socket import ConnectMixin
from plib.io.async import AsyncConnectMixin, PersistentMixin


class PersistentSocketMixin(AsyncConnectMixin, ConnectMixin, PersistentMixin):
    """Mixin class for persistent, full-duplex asynchronous socket I/O.
    
    Can be used for both clients and servers, but intended
    mainly for clients that need connect functionality. (For
    server-side persistent sockets, you should normally use the
    ``PersistentRequestHandler`` class with ``SocketServer``.)
    """
    pass

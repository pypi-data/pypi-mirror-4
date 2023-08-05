#!/usr/bin/env python
"""
Module SocketClientMixin
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous SocketClientMixin class;
this class is factored out from SocketClient so that alternate
read/write handling can be mixed in.
"""

from plib.io.socket import BaseClient
from plib.io.async import AsyncConnectMixin, ClientMixin


class SocketClientMixin(AsyncConnectMixin, BaseClient, ClientMixin):
    """Asynchronous socket client mixin class.
    """
    pass

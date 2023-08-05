#!/usr/bin/env python
"""
Module ServerMixin
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous ServerMixin class.
"""

from plib.io.async import AsyncCommunicator
from plib.io.comm import ServerCommunicator


class ServerMixin(AsyncCommunicator, ServerCommunicator):
    """Mixin class for async server-side I/O channel.
    """
    pass

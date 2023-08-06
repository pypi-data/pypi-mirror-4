#!/usr/bin/env python
"""
Module SerialServerMixin
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous SerialServerMixin class.
"""

from plib.io.serial import BaseServer
from plib.io.async import ServerMixin


class SerialServerMixin(BaseServer, ServerMixin):
    """Asynchronous server-side serial I/O mixin class.
    """
    pass

#!/usr/bin/env python
"""
Module SerialClientMixin
Sub-Package IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the blocking I/O SerialClientMixin class.
"""

from plib.io.serial import BaseClient
from plib.io.blocking import ClientMixin


class SerialClientMixin(BaseClient, ClientMixin):
    """Mixin class for client-side blocking serial I/O.
    """
    pass

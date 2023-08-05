#!/usr/bin/env python
"""
Module SerialClientMixin
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous SerialClientMixin class.
"""

from plib.io.serial import BaseClient
from plib.io.async import ClientMixin


class SerialClientMixin(BaseClient, ClientMixin):
    """Mixin class for async serial client.
    
    Call the ``client_communicate method`` to open a serial
    device and send data; override the ``process_data`` method
    to do something with the reply.
    """
    pass

#!/usr/bin/env python
"""
Module BaseClient
Sub-Package IO.SERIAL of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the serial BaseClient class.
"""


class BaseClient(object):
    """Base class for serial I/O clients.
    """
    
    def setup_client(self, devid):
        """Open the serial device ID.
        """
        if not self.port:
            self.create_port(devid)

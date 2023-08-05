#!/usr/bin/env python
"""
Module BaseServer
Sub-Package IO.SERIAL of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the serial BaseServer class.
"""


class BaseServer(object):
    """Base class for serial I/O servers.
    
    Assumes that a subclass of ``ServerCommunicator``
    is earlier in the MRO, to provide the
    ``run_loop`` method. A serial server
    directly talks to one client at a time, so it
    just has to run the comm loop to do so. The only
    other functionality here is to ensure that the
    channel is closed when the loop exits.
    """
    
    def serve_forever(self, callback=None):
        try:
            self.run_loop(callback)
        finally:
            self.close()

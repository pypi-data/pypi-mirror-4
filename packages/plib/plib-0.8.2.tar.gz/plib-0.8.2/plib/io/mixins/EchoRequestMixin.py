#!/usr/bin/env python
"""
Module EchoRequestMixin
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``EchoRequestMixin`` class. This
is a request handler mixin class that echoes received data
back to the client.
"""


class EchoRequestMixin(object):
    """Echo request handler mixin class.
    
    Echoes received data back to client. Can be mixed in
    with any request handler class.
    """
    
    def process_data(self):
        """Echo data back to client.
        
        If there is no data, don't echo (it means the client
        has closed the connection).
        """
        
        if self.read_data:
            self.start(self.read_data)

#!/usr/bin/env python
"""
Sub-Package IO.BASE of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package includes the base classes for the three
types of I/O objects: I/O, data, and communication.
"""

from plib.stdlib.util import ModuleProxy

ModuleProxy(__name__).init_proxy(__name__, __path__, globals(), locals())

# Now clean up our namespace
del ModuleProxy

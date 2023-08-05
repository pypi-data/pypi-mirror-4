#!/usr/bin/env python
"""
Sub-Package STDLIB.CLASSES of Package PLIB -- Python Class Objects
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains the ``StateMachine`` and
``TokenConverter`` classes.
"""

from plib.stdlib.util import ModuleProxy

from ._defs import *

excludes = ['_defs']

ModuleProxy(__name__).init_proxy(__name__, __path__, globals(), locals(),
    excludes=excludes)

# Now clean up our namespace
del ModuleProxy

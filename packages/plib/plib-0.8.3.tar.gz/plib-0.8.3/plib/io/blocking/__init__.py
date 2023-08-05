#!/usr/bin/env python
"""
Sub-Package IO.BLOCKING of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package includes classes for handling blocking
I/O, including both serial and socket I/O channels. See
the docstring for the parent package, ``plib.io``,
for information on how this package fits into the overall
I/O package structure.
"""

from plib.io.utils import IOModuleProxy

IOModuleProxy(__name__).init_proxy(__name__, __path__, globals(), locals())

# Now clean up our namespace
del IOModuleProxy

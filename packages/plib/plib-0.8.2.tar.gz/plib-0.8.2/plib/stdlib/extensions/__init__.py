#!/usr/bin/env python
"""
Sub-Package STDLIB.EXTENSIONS of Package PLIB -- Python/C Extensions
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains extensions written using the
Python/C API. Currently the following extensions are
implemented:

function ``cobject_compare``: takes two CObjects and returns a
    ``bool`` indicating whether they wrap the same C-level pointer.
"""

from ._extensions import *

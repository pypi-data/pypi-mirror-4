#!/usr/bin/env python
"""
Module IMP -- Import Helper Functions
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the following helper function for
importing objects:

function import_from_module -- import_module, plus a getattr call to
    retrieve the named attribute from the dotted module; the equivalent
    of 'from x.y.z import a' (except that module a of package x.y.z
    will not be returned unless it has already been imported into the
    namespace of x.y.z)
"""

from importlib import import_module


def import_from_module(modname, attrname):
    """Return the module attribute pointed to by from x.y.z import a.
    """
    return getattr(import_module(modname), attrname)

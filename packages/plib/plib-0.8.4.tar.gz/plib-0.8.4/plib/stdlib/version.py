#!/usr/bin/env python
"""
Module VERSION -- Version Numbering Utilities
Sub-Package STDLIB of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains functions for manipulating version
number strings and tuples, using an extension of the
distutils StrictVersion class.
"""

import re
import string

from distutils.version import StrictVersion


class PVersion(StrictVersion):
    """Extended distutils version class.
    
    Extension of StrictVersion that takes a tuple as a
    constructor argument. The tuple is expected to be
    of the form (major, minor, patch, <prerelease>),
    where <prerelease> is either None or a 2-tuple
    (prerelease, prerelease_num). The patch element
    may be either None or an integer; the major and
    minor elements must be integers or ValueError will
    be thrown. The prerelease element must be a string
    starting with 'a' or 'b'; the prerelease_num element
    must be an integer.
    """
    
    def _error_exit(self, ver):
        raise ValueError, "Version tuple %s is invalid." % str(ver)
    
    def __init__(self, ver):
        if isinstance(ver, tuple):
            # Hack to make it look like the tuple is a product
            # of self.parse
            
            try:
                major, minor, patch, tail = ver + tuple(
                    [None for x in range(4 - len(ver))])
                
                if patch is None:
                    patch = 0
                
                if tail:
                    suffix, suffixnum = tail
                    if suffix not in ('a', 'b'):
                        raise ValueError
                else:
                    suffix = None
                    suffixnum = 0
                
                self.version = tuple(map(int, [major, minor, patch]))
                
                if suffix is not None:
                    suffix = suffix[0]
                    self.prerelease = (suffix, int(suffixnum))
                else:
                    self.prerelease = None
            
            except (TypeError, ValueError):
                self._error_exit(ver)
            
            ver = None
        
        StrictVersion.__init__(self, ver)


def version_string(ver_t):
    """Return a properly formatted version string from a tuple.
    """
    return str(PVersion(ver_t))

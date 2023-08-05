#!/usr/bin/env python
"""
Module _EXTRAS -- Enhancing the builtin namespace
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

import sys
from operator import mul as _mul


def first(iterable, default=None):
    """Return first item in iterable, or default if empty.
    """
    for item in iterable:
        return item
    return default


def inverted(mapping, keylist=None):
    """Return a mapping that is the inverse of the given mapping.
    
    The optional argument ``keylist`` limits the keys that are inverted.
    """
    if keylist is not None:
        return mapping.__class__((mapping[key], key)
            for key in keylist)
    return mapping.__class__((value, key)
        for key, value in mapping.iteritems())


def last(iterable, default=None):
    """Return last item in iterable, or default if empty.
    """
    result = default
    for item in iterable:
        result = item
    return result


def prod(iterable, mul=_mul):
    """Return the product of all items in iterable.
    """
    return reduce(mul, iterable, 1)


def type_from_name(name):
    """Return type object corresponding to ``name``.
    
    Currently searches only the built-in types. No checking is done to
    make sure the returned object is actually a type.
    """
    import __builtin__
    try:
        return getattr(__builtin__, name)
    except AttributeError:
        raise ValueError, "no type corresponding to %s" % name

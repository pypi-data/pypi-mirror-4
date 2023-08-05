#!/usr/bin/env python
"""
Module OSTOOLS -- PLIB Operating System Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains utilities similar to those provided
in the standard library ``os`` module.

Utility functions currently provided:

locate -- generator that yields all filenames starting at a
    root location (by default, the current directory) that match
    a given pattern.

subdirs -- generator that yields all subdirectories of the
    given path (by default, the current directory).
"""

import os
import fnmatch


def _gen_names(path, seq, pattern):
    for name in (os.path.abspath(os.path.join(path, item))
        for item in seq if fnmatch.fnmatch(item, pattern)):
            yield name


def locate(pattern, root=None, include_dirs=False):
    """
    Generates all filenames in the directory tree starting at
    root that match pattern. Does not include subdirectories by
    default; this can be overridden with the include_dirs
    parameter. If subdirectories are included, they are yielded
    before regular files in the same directory.
    """
    
    root = root or os.getcwd()
    for path, dirs, files in os.walk(root):
        if include_dirs:
            for name in _gen_names(path, dirs, pattern):
                yield name
        for name in _gen_names(path, files, pattern):
            yield name


def subdirs(path=None, fullpath=False, include_hidden=False):
    """Generate subdirectories of path.
    
    The ``fullpath`` keyword argument determines whether the
    full pathname is returned for each subdir; it defaults
    to not doing so (i.e., just returning the bare subdir
    name).
    
    The ``include_hidden`` keyword argument determines whether
    hidden subdirectories (those beginning with a dot .) are
    included; the default is not to include them.
    """
    
    path = path or os.getcwd()
    for entry in os.listdir(path):
        subpath = os.path.join(path, entry)
        if os.path.isdir(subpath):
            if include_hidden or not entry.startswith('.'):
                yield (entry, subpath)[fullpath]

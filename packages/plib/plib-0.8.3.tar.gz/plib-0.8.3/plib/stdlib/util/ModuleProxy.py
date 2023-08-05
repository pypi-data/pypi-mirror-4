#!/usr/bin/env python
"""
Module ModuleProxy
Sub-Package STDLIB.UTIL of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ModuleProxy class. For examples
of intended use cases for this class, check out the
``main.py`` module in the PLIB.GUI sub-package, or any
of a number of ``__init__.py`` modules in the PLIB.IO
sub-packages. The docstrings and comments there give more
information.

One note about usage: whenever importing from a package
that uses this functionality, absolute imports should be
used. Using relative imports risks running afoul of the
name ambiguity between the object you want to import (a
class, usually) and the module it's defined in. Absolute
imports are "purer" anyway, so this is not viewed as a
bothersome restriction. (In Python 3.0, explicit relative
imports with a leading dot . will become standard, and
this restriction may be lifted.)
"""

import sys
import os
import glob
import types


# Helper function for lazy loading of actual modules

def module_helper(modname, globals_dict, locals_dict):
    def f():
        result = __import__(modname, globals_dict, locals_dict)
        return getattr(result, modname)
    f.__name__ = "%s_helper" % modname
    return f


# Note that we subclass types.ModuleType in order to fool
# various introspection utilities (e.g., pydoc and the builtin
# 'help' command in the interpreter) into thinking ModuleProxy
# instances are actual modules. Among other things, this is
# necessary for the builtin 'help' command to properly display
# the info from the proxied module's docstring (setting the
# proxy's __doc__ to the actual module's __doc__ is *not*
# enough to do this by itself); note also that we don't
# override the constructor because various Python internals
# expect module objects to have a particular signature for
# the constructor; instead, we add the init_proxy method which
# must be called immediately on constructing the object to do
# the proxying magic

class ModuleProxy(types.ModuleType):
    
    def init_proxy(self, name, path, globals_dict, locals_dict,
            names=None, excludes=None, autodiscover=True):
        
        self._excludes = excludes
        
        names = dict(names or {})
        excludes = set(excludes or [])
        
        if autodiscover:
            for pathname in path:
                for filename in glob.glob(os.path.join(pathname, "*.py")):
                    modname = os.path.splitext(os.path.basename(filename))[0]
                    if not self._exclude(modname, excludes):
                        names[modname] = module_helper(modname,
                            globals_dict, locals_dict)
        
        self._names = names
        
        # Monkeypatch sys.modules with the proxy object (make
        # sure we store a reference to the real module first!)
        self._mod = sys.modules[name]
        sys.modules[name] = self
        
        # Pass-through module's docstring (this attribute name
        # appears in both so __getattr__ below won't handle it);
        # as noted above, this in itself isn't enough to make
        # the 'help' builtin work right, but it is a necessary
        # part of doing so
        self.__doc__ = self._mod.__doc__
    
    def __repr__(self):
        return "<proxy of module '%s' from '%s'>" % \
            (self._mod.__name__, self._mod.__file__)
    
    def _exclude(self, name, excludes):
        # This allows customization of the exclusion algorithm; by
        # default we exclude names in the excludes set and private
        # names (ones that start with '_')
        return (name in excludes) or name.startswith('_')
    
    def _get_name(self, name):
        names = self.__dict__['_names']
        result = names[name]
        
        # This hack allows features like 'lazy importing' to work;
        # a callable names dict entry allows arbitrary (and possibly
        # expensive) processing to take place only when the attribute
        # is first accessed, instead of when the module is initially
        # imported. Also, since we store the result in our __dict__,
        # the expensive function won't get called again, so we are
        # essentially memoizing the result.
        if hasattr(result, '__call__'):
            result = result()
        
        setattr(self, name, result)
        del names[name]
        return result
    
    def __getattr__(self, name):
        try:
            # Remember we need to return the real module's attributes!
            mod_result = getattr(self._mod, name)
        except AttributeError:
            try:
                our_result = self._get_name(name)
            except (KeyError, ValueError, AttributeError):
                raise AttributeError("%s object has no attribute %s" %
                    (self, name))
            else:
                return our_result
        else:
            return mod_result

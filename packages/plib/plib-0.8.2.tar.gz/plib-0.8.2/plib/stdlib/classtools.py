#!/usr/bin/env python
"""
Module CLASSTOOLS -- Utilities for Python Classes
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains some helpful utilities for working
with Python classes. It currently provides:

recurselist, recursedict -- when you have a class field that's
    a container, these functions provide a way of combining all
    the values in your class's MRO, so you don't have to repeat
    them in derived classes.

Singleton -- class that only allows a single instance.
"""


def _recurse(klass, name, result, methodname):
    method = getattr(result, methodname)
    for c in klass.__mro__:
        if name in c.__dict__:
            method(c.__dict__[name])
    return result


def recurselist(klass, name):
    """
    Recurses through mro of klass, assuming that where
    the class attribute name is found, it is a list;
    returns a list concatenating all of them.
    """
    return _recurse(klass, name, [], 'extend')


def recursedict(klass, name):
    """
    Recurses through mro of klass, assuming that where
    the class attribute name is found, it is a dict;
    returns a dict combining all of them.
    """
    return _recurse(klass, name, {}, 'update')


class Singleton(object):
    """Each subclass of this class can have only a single instance.
    
    (Taken from Guido's new-style class intro essay.)
    """
    
    def __new__(cls, *args, **kwds):
        """Only create an instance if it isn't already there.
        """
        
        inst = cls.__dict__.get("__inst__")
        if inst is None:
            cls.__inst__ = inst = object.__new__(cls)
            inst._init(*args, **kwds)
        return inst
    
    def _init(self, *args, **kwds):
        """Override this to do customized initialization.
        
        (This method will only be called once, whereas __init__ will
        be called each time the class constructor is called).
        """
        pass

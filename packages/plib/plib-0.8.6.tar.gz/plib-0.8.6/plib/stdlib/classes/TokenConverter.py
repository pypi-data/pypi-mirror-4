#!/usr/bin/env python
"""
Module TokenConverter
Sub-Package STDLIB.CLASSES of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the TokenConverter class, which
automates data conversion between a fixed-length list of
data objects and string tokens that represent them.
"""

from plib.stdlib.coll import abstractsequence


class TokenConverter(abstractsequence):
    """Sequence wrapper for a collection of named string tokens.
    
    Sequence class that initializes itself from a list of string tokens;
    it uses a list of tuples (the converters field) to convert each token to
    the appropriate data type and store it in a named attribute. The data
    can then be accessed as a sequence of string tokens, or through each
    named attribute as the appropriate native data type. The purpose is to
    automate the storage and retrieval of the data from simple text files
    as string tokens, while allowing native-type operations on the data
    (such as arithmetic on numbers and dates) to be easily done while the
    data is loaded.
    
    The converters class field in subclasses must be filled with a list of
    2-tuples of the form (attr_name, convert_func), giving the name of the
    attribute of this object that will store the data, and the data type
    conversion function which takes a single string argument and returns
    the value converted to the desired data type.
    
    Note that there is no length-checking on the list of tokens passed to
    the constructor; passing a list of tokens that is longer than the list
    of converters will result in an IndexError. Also, although the class
    is only designed to support integer indexes (not slices), no type
    checking is done on indexes, so the behavior if slice indexes are used
    is not guaranteed.
    """
    
    converters = None
    default_value = ""
    
    def __init__(self, tokens=None):
        assert self.converters is not None
        self.names = frozenset(c[0] for c in self.converters)
        
        # This ensures that the __setitem__ code in abstractsequence
        # will work when we populate the sequence below (__setitem__
        # uses __getitem__ to check that the requested index is valid)
        for name in self.names:
            setattr(self, name, self.default_value)
        
        # Now we can populate from the given tokens
        for index, token in enumerate(tokens or []):
            self[index] = token
    
    def __len__(self):
        return len(self.converters)
    
    def __getitem__(self, index):
        return str(getattr(self, self.converters[index][0]))
    
    def set_index(self, index, value):
        setattr(self,
            self.converters[index][0], self.converters[index][1](value))

#! /usr/bin/env python
"""
Module PIniFile
Sub-Package STDLIB.INI of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``PIniFile`` class.
"""

from .PIniFileBase import PIniFileBase


class PIniFile(PIniFileBase):
    """OS-independent class for an actual preferences file.
    
    Keeps a dictionary of (section name, option name) tuples vs. get/set
    functions to link the preferences to program actions. Provides
    three API methods for applications to use, as noted in the
    module documentation above: buildini, readini, and writeini.
    Also provides options parameter to constructor and _optionlist
    class field to allow automatic loading of options by either method.
    The _autoload and _autosave class fields allow control of whether
    options are loaded/saved when the class instance is
    constructed/destructed (normally the default behavior is fine
    but there may be cases where the timing of these events needs to
    be altered).
    
    FIXME: calling writeini() in __del__ causes a TypeError
    exception 'unsubscriptable object', so _autosave is currently
    not functional if True.
    """
    
    _optionlist = None
    _autoload = True
    _autosave = False
    
    def __init__(self, iname, options=None):
        PIniFileBase.__init__(self, iname)
        self.vardict = {}
        if options:
            self._optionlist = options
        if self._optionlist is not None:
            self.buildini(self._optionlist)
            if self._autoload:
                self.readini()
    
    #def __del__(self):
    #    if self._autosave:
    #        self.writeini()
    
    def buildini(self, buildlist):
        """ Called with a "list of lists" of sections and options to
        set up the preferences file """
        for sect in buildlist:
            self.addsection(sect[0])
            for opt in sect[1]:
                self.addoption(sect[0], opt[0], opt[1], opt[2])
                if len(opt) > 4:
                    entry = (opt[3], opt[4])
                elif len(opt) > 3:
                    entry = opt[3]
                else:
                    entry = "%s_%s" % (sect[0], opt[0])
                self.vardict[(sect[0], opt[0])] = entry
    
    def readini(self):
        """Read preferences from file and feed them to the program.
        """
        self.readvalues()
        for key in self.vardict.iterkeys():
            entry = self.vardict[key]
            value = self.getvalue(key[0], key[1])
            if isinstance(entry, tuple):
                entry[1](value)
            else:
                setattr(self, entry, value)
    
    def writeini(self):
        """Get preferences data from the program and write to file.
        """
        for key in self.vardict.iterkeys():
            entry = self.vardict[key]
            if isinstance(entry, tuple):
                value = entry[0]()
            else:
                value = getattr(self, entry)
            self.setvalue(key[0], key[1], value)
        self.writevalues()

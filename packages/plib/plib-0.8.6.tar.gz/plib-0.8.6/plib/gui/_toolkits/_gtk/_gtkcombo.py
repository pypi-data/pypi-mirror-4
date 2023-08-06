#!/usr/bin/env python
"""
Module GTKCOMBO -- Python GTK Combo Box Widgets
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI objects for combo boxes.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from plib.gui.defs import *
from plib.gui._widgets import _helpers, combo

from _gtkcommon import _PGtkMeta, _PGtkWidget, _gtksignals


# TODO: determine if gtk.ComboBox can be used
class PGtkComboBox(gtk.ComboBoxEntry, _PGtkWidget,
        _helpers._PShift, combo.PComboBoxBase):
    
    __metaclass__ = _PGtkMeta
    
    #_adjust = True
    
    # Define selected signal using 'automagic' class field
    __gsignals__ = { _gtksignals[SIGNAL_SELECTED]:
        (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_INT,)) }
    
    def __init__(self, parent, sequence=None, target=None, geometry=None):
        _helpers._PShift.__init__(self)
        self._model = gtk.ListStore(gobject.TYPE_STRING)
        gtk.ComboBoxEntry.__init__(self, self._model, 0)
        self.child.set_editable(False) # prevent editing text in cell
        _PGtkWidget.__init__(self, parent)
        combo.PComboBoxBase.__init__(self, sequence, target, geometry)
        
        # The changed signal doesn't include the current index, so we
        # gateway it
        self._initialized = False  # prevent firing an extra signal at startup
        self.connect("changed", self.changed_selection)
    
    def changed_selection(self, obj):
        if self._initialized:
            self.do_notify(SIGNAL_SELECTED, self.get_active())
        else:
            self._initialized = True
    
    def __iter__(self):
        """ Need to override gtk.ComboBoxEntry's iter method. """
        return combo.PComboBoxBase.__iter__(self)
    
    def __len__(self):
        """ Need to override gtk.ComboBoxEntry's len method. """
        return _helpers._PShift.__len__(self)
    
    def _get_data(self, index):
        return self._model.get_value(self._items[index], 0)
    
    def _set_data(self, index, value):
        self._model.set_value(self._items[index], 0, value)
    
    def _add_data(self, index, value):
        if index == self.__len__():
            self._items[index] = self._model.append((value,))
        else:
            before = self._items[index]
            self._shiftright(index)
            self._items[index] = self._model.insert_before(before, (value,))
    
    def _del_data(self, index):
        self_model.remove(self._items[index])
        del self._items[index]
        self._shiftleft(index)
    
    def current_index(self):
        return self.get_active()
    
    def set_current_index(self, index):
        self.set_active(index)

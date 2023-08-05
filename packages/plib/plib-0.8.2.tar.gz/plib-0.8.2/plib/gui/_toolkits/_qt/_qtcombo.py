#!/usr/bin/env python
"""
Module QTCOMBO -- Python Qt Combo Box Widgets
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for combo boxes.
"""

import qt

from plib.gui._widgets import combo

from _qtcommon import _PQtMeta, _PQtWidget


class PQtComboBox(qt.QComboBox, _PQtWidget, combo.PComboBoxBase):
    
    __metaclass__ = _PQtMeta
    
    widget_class = qt.QComboBox
    
    def __init__(self, parent, sequence=None, target=None, geometry=None):
        qt.QComboBox.__init__(self, False, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        combo.PComboBoxBase.__init__(self, sequence, target, geometry)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt buttons don't appear to fully respect QSizePolicy.Fixed
        self.setMinimumWidth(width)
    
    def current_text(self):
        return str(self.currentText())
    
    # Note that there's no quick override for set_current_text in Qt; the
    # corresponding method to the above doesn't do what we want (it changes
    # the stored text in the combo instead of selecting the text we give it)
    
    def current_index(self):
        return self.currentItem()
    
    def set_current_index(self, index):
        self.setCurrentItem(index)
    
    def count(self, value):
        # Method name collision, we want it to be the Python sequence
        # count method here.
        return combo.PComboBoxBase.count(self, value)
    
    def _indexlen(self):
        # Let this method access the Qt combo box count method.
        return qt.QComboBox.count(self)
    
    def _get_data(self, index):
        return str(self.text(index))
    
    def _set_data(self, index, value):
        self.changeItem(str(value), index)
    
    def _add_data(self, index, value):
        if index == self.__len__():
            self.insertItem(str(value))
        else:
            self.insertItem(str(value), index)
    
    def _del_data(self, index):
        self.removeItem(index)

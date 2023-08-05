#!/usr/bin/env python
"""
Module KDECOMBO -- Python KDE Combo Box Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for combo boxes.
"""

import qt
import kdeui

from plib.gui._widgets import combo

from _kdecommon import _PKDEMeta, _PKDEWidget


class PKDEComboBox(kdeui.KComboBox, _PKDEWidget, combo.PComboBoxBase):
    
    __metaclass__ = _PKDEMeta
    
    widget_class = kdeui.KComboBox
    
    def __init__(self, parent, sequence=None, target=None, geometry=None):
        kdeui.KComboBox.__init__(self, False, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        combo.PComboBoxBase.__init__(self, sequence, target, geometry)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt buttons don't appear to fully respect QSizePolicy.Fixed
        self.setMinimumWidth(width)
    
    def current_text(self):
        return str(self.currentText())
    
    # Note that there's no quick override for set_current_text in KDE; the
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
        # Let this method access the KDE combo box count method.
        return kdeui.KComboBox.count(self)
    
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

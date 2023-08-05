#!/usr/bin/env python
"""
Module WXCOMBO -- Python wxWidgets Combo Box Widgets
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for combo boxes.
"""

import wx

from plib.gui.defs import *
from plib.gui._widgets import combo

from _wxcommon import _PWxWidget


# TODO: determine if simple combo without edit cell can be used
class PWxComboBox(wx.ComboBox, _PWxWidget, combo.PComboBoxBase):
    
    def __init__(self, parent, sequence=None, target=None, geometry=None):
        wx.ComboBox.__init__(self, parent,
            style=(wx.CB_DROPDOWN | wx.CB_READONLY))
        self._align = ALIGN_LEFT # used by PWxPanel to determine placement
        combo.PComboBoxBase.__init__(self, sequence, target, geometry)
    
    def current_text(self):
        return self.GetStringSelection()
    
    def set_current_text(self, text):
        self.SetStringSelection(text)
    
    def current_index(self):
        return self.GetSelection()
    
    def set_current_index(self, index):
        self.SetSelection(index)
    
    def _indexlen(self):
        return self.GetCount()
    
    def _get_data(self, index):
        return self.GetString(index)
    
    def _set_data(self, index, value):
        self.SetString(index, value)
    
    def _add_data(self, index, value):
        if index == self.__len__():
            self.Append(value)
        else:
            self.Insert(value, index)
    
    def _del_data(self, index):
        self.Delete(index)

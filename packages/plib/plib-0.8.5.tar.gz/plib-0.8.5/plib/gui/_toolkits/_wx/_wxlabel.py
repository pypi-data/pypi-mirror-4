#!/usr/bin/env python
"""
Module WXLABEL -- Python wxWidgets Text Label Widgets
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for text label widgets.
"""

import wx

from plib.gui.defs import *
from plib.gui._widgets import label

from _wxcommon import _PWxWidget


class PWxTextLabel(wx.StaticText, _PWxWidget, label.PTextLabelBase):
    
    def __init__(self, parent, text=None, geometry=None):
        wx.StaticText.__init__(self, parent)
        self._align = ALIGN_LEFT
        label.PTextLabelBase.__init__(self, text, geometry)
    
    def get_text(self):
        return self.GetLabel()
    
    def set_text(self, value):
        self.SetLabel(value)

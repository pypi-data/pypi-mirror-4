#!/usr/bin/env python
"""
Module WXDISPLAY -- Python wxWidgets Text Display Widgets
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for text display widgets.
"""

import wx

from plib.gui.defs import *
from plib.gui._widgets import display

from _wxcommon import _PWxWidget, _wx_ec_scroll_style


class PWxTextDisplay(wx.TextCtrl, _PWxWidget, display.PTextDisplayBase):
    
    _style = wx.TE_MULTILINE | wx.TE_PROCESS_TAB
    
    def __init__(self, parent, text=None, geometry=None, scrolling=False):
        self._expand = True
        self._align = ALIGN_JUST
        if scrolling:
            self._style = self._style | _wx_ec_scroll_style
        wx.TextCtrl.__init__(self, parent, style=self._style)
        self.SetEditable(False)
        display.PTextDisplayBase.__init__(self, text, geometry)
    
    def get_text(self):
        return self.GetValue()
    
    def set_text(self, value):
        self.SetValue(value)

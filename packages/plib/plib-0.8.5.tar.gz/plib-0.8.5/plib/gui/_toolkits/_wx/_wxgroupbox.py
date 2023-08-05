#!/usr/bin/env python
"""
Module WXGROUPBOX -- Python wxWidgets Group Box Widgets
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for group box widgets.
"""

import wx

from plib.gui.defs import *
from plib.gui._widgets import groupbox

from _wxcommon import _PWxWidget


class PWxGroupBox(wx.Panel, _PWxWidget, groupbox.PGroupBoxBase):
    
    def __init__(self, parent, caption, controls=None,
            margin=-1, spacing=-1, geometry=None):
        
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        self._align = ALIGN_TOP
        self._expand = True
        self._margin = margin
        self._spacing = spacing
        self._haswidgets = False
        self._box = wx.StaticBox(self)
        self._boxsizer = wx.StaticBoxSizer(self._box, wx.VERTICAL)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self._boxsizer, 1, wx.EXPAND, 0)
        groupbox.PGroupBoxBase.__init__(self, parent, caption, controls,
            margin, spacing, geometry)
    
    def set_caption(self, caption):
        self._box.SetLabel(caption)
    
    def set_margin(self, margin):
        # Margin is dealt with differently in wxWidgets, see above
        pass
    
    def set_spacing(self, spacing):
        # Spacing is dealt with differently in wxWidgets, see above
        pass
    
    def _add_control(self, control):
        # Somewhat abbreviated version of the cruft in PWxPanel
        
        if self._haswidgets:
            if self._spacing > -1:
                self._boxsizer.AddSpacer(self._spacing)
        elif self._margin > -1:
            self._boxsizer.AddSpacer(self._margin)
        
        if hasattr(control, '_align') and (control._align != ALIGN_JUST):
            proportion = 0
            flag = wx.ALIGN_TOP
        else:
            proportion = 1
            flag = 0
        
        if hasattr(control, '_expand') and control._expand:
            flag |= wx.EXPAND
        
        flag |= wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT
        
        self._boxsizer.Add(control, proportion, flag, self._margin)
        if not self._haswidgets:
            self._haswidgets = True
    
    def _dolayout(self):
        if self._margin > -1:
            self._boxsizer.AddSpacer(self._margin)
        self.SetSizerAndFit(self._sizer)

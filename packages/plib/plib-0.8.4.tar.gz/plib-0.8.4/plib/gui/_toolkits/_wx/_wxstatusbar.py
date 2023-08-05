#!/usr/bin/env python
"""
Module WXSTATUSBAR -- Python wxWidgets Status Bar Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for the status bar.
"""

import wx

from plib.gui._base import statusbar

from _wxcommon import _PWxWidgetBase
#from _wxlabel import PWxTextLabel


class PWxStatusBar(wx.StatusBar, _PWxWidgetBase, statusbar.PStatusBarBase):
    
    #textareaclass = PWxTextLabel # FIXME: not needed for wx?
    
    def __init__(self, parent, widgets=None):
        wx.StatusBar.__init__(self, parent)
        self.SetFieldsCount(1) # FIXME: add fields for 'widgets' below
        self.SetStatusWidths([-1])
        statusbar.PStatusBarBase.__init__(self, parent, widgets)
    
    def _add_widget(self, widget, expand=False, custom=True):
        # FIXME: No custom widgets in wx?
        pass
    
    def get_text(self):
        return self.GetStatusText(0)
    
    def set_text(self, value):
        self.SetStatusText(value, 0)

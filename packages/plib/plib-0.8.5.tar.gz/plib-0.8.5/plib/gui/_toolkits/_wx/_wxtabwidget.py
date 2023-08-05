#!/usr/bin/env python
"""
Module WXTABWIDGET -- Python wxWidgets Tab Widget
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for the tab widget.
"""

import wx

from plib.gui.defs import *
from plib.gui._widgets import tabwidget

from _wxcommon import _PWxClientWidget


class PWxTabWidget(wx.Notebook, _PWxClientWidget, tabwidget.PTabWidgetBase):
    
    def __init__(self, parent, tabs=None, target=None):
        wx.Notebook.__init__(self, parent)
        self._align = ALIGN_JUST # used by PWxPanel to determine placement
        self._expand = True
        tabwidget.PTabWidgetBase.__init__(self, parent, tabs, target)
    
    def __len__(self):
        return self.GetPageCount()
    
    def _get_tabtitle(self, index):
        return self.GetPageText(index)
    
    def _set_tabtitle(self, index, title):
        self.SetPageText(index, title)
    
    def _add_tab(self, index, title, widget):
        if index == self.__len__():
            self.AddPage(widget, title)
        else:
            self.InsertPage(index, widget, title)
    
    def _del_tab(self, index):
        self.RemovePage(index)
    
    def current_index(self):
        return self.GetSelection()
    
    def set_current_index(self, index):
        self.SetSelection(index)

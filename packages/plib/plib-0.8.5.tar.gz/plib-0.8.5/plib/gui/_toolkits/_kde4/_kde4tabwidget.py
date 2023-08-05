#!/usr/bin/env python
"""
Module KDETABWIDGET -- Python KDE Tab Widget
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for the tab widget.
"""

from PyKDE4 import kdeui

from plib.gui._widgets import tabwidget

from _kde4common import _PKDEMeta, _PKDEClientWidget


class PKDETabWidget(kdeui.KTabWidget, _PKDEClientWidget,
        tabwidget.PTabWidgetBase):
    
    __metaclass__ = _PKDEMeta
    
    widget_class = kdeui.KTabWidget
    
    def __init__(self, parent, tabs=None, target=None):
        self._item = None
        self._target = None
        self._setting_index = False
        kdeui.KTabWidget.__init__(self, parent)
        tabwidget.PTabWidgetBase.__init__(self, parent, tabs, target)
    
    def count(self, value):
        # Method name collision, we want it to be the Python sequence
        # count method here.
        return tabwidget.PTabWidgetBase.count(self, value)
    
    def __len__(self):
        # Let this method access the KDE tab widget count method.
        return kdeui.KTabWidget.count(self)
    
    def _get_tabtitle(self, index):
        return str(self.tabText(index))
    
    def _set_tabtitle(self, index, title):
        self.setTabText(index, str(title))
    
    def _add_tab(self, index, title, widget):
        self.insertTab(index, widget, str(title))
    
    def _del_tab(self, index):
        self.removeTab(index)
    
    def current_index(self):
        return self.currentIndex()
    
    def _current_changed(self, index):
        # Wrapper for tab changed signal.
        if self._setting_index:
            self._item = self.widget(index)
        elif self._target:
            self._target(self._item or self.widget(index))
    
    def connect_to(self, target):
        # Hack to capture double firing of tab changed signal when
        # tab is changed programmatically instead of by user (this
        # also conveniently allows us to change the method signature
        # so the target can still take the item as an argument).
        self._target = target
        tabwidget.PTabWidgetBase.connect_to(self, self._current_changed)
    
    def set_current_index(self, index):
        # Wrap the call to avoid double calling of signal handler, then
        # make the call by hand.
        self._setting_index = True
        self.setCurrentIndex(index)
        self._setting_index = False
        self._current_changed(index)
        self._item = None

#!/usr/bin/env python
"""
Module QTTABWIDGET -- Python Qt Tab Widget
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for the tab widget.
"""

import qt

from plib.gui._widgets import tabwidget

from _qtcommon import _PQtMeta, _PQtClientWidget


class PQtTabWidget(qt.QTabWidget, _PQtClientWidget,
        tabwidget.PTabWidgetBase):
    
    __metaclass__ = _PQtMeta
    
    widget_class = qt.QTabWidget
    
    def __init__(self, parent, tabs=None, target=None):
        self._item = None
        self._target = None
        self._setting_index = False
        qt.QTabWidget.__init__(self, parent)
        tabwidget.PTabWidgetBase.__init__(self, parent, tabs, target)
    
    def count(self, value):
        # Method name collision, we want it to be the Python sequence
        # count method here.
        return tabwidget.PTabWidgetBase.count(self, value)
    
    def __len__(self):
        # Let this method access the Qt tab widget count method.
        return qt.QTabWidget.count(self)
    
    def _get_tabtitle(self, index):
        return str(self.tabLabel(self._items[index]))
    
    def _set_tabtitle(self, index, title):
        self.setTabLabel(self._items[index], str(title))
    
    def _add_tab(self, index, title, widget):
        self.insertTab(widget, str(title), index)
    
    def _del_tab(self, index):
        self.removePage(self._items[index])
    
    def current_index(self):
        return self.currentPageIndex()
    
    def _current_changed(self, item):
        # Wrapper for tab changed signal.
        if self._setting_index:
            self._item = item
        elif self._target:
            self._target(item)
    
    def connect_to(self, target):
        # Hack to capture double firing of tab changed signal when
        # tab is changed programmatically instead of by user.
        self._target = target
        tabwidget.PTabWidgetBase.connect_to(self, self._current_changed)
    
    def set_current_index(self, index):
        # Wrap the call to avoid double calling of signal handler, then
        # make the call by hand.
        self._setting_index = True
        self.setCurrentPage(index)
        self._setting_index = False
        self._current_changed(self._item)
        self._item = None

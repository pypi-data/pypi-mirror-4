#!/usr/bin/env python
"""
Module TABWIDGET -- GUI Tab Widget
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for a tab widget.
"""

from plib.stdlib.coll import baselist

from plib.gui.defs import *
from plib.gui._widgets import _helpers
from plib.gui._widgets import _signal


class PTabWidgetBase(_signal._PNotifyControl, _helpers._PShift, baselist):
    """Tab widget as a Python list of 2-tuples (tab-title, widget).
    """
    
    signal = SIGNAL_TABCHANGED
    
    def __init__(self, parent, tabs=None, target=None):
        self._parent = parent
        _signal._PNotifyControl.__init__(self, target)
        _helpers._PShift.__init__(self)
        baselist.__init__(self)
        if tabs is not None:
            self._createtabs(tabs)
    
    def _createtabs(self, tabs):
        """Create tabs from sequence.
        
        Assumes that the sequence contains tuples of (title, widget)
        for each tab.
        """
        self.extend(tabs)
    
    def _get_tabtitle(self, index):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def _set_tabtitle(self, index, title):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _add_tab(self, index, title, widget):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _del_tab(self, index):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _get_data(self, index):
        return (self._get_tabtitle(index), self._items[index])
    
    def _set_data(self, index, value):
        # This gets a little complicated because we have to delete the
        # old tab at this index and insert a new one.
        self._del_data(index)
        self._add_data(index, value)
    
    def _add_data(self, index, value):
        self._shiftright(index)
        self._items[index] = value[1]
        self._add_tab(index, value[0], value[1])
    
    def _del_data(self, index):
        self._del_tab(index)
        del self._items[index]
        self._shiftleft(index)
    
    def current_index(self):
        """Return the currently selected tab index.
        
        Derived classes must implement.
        """
        raise NotImplementedError
    
    def set_current_index(self, index):
        """Set the currently selected tab index.
        
        Derived classes must implement.
        """
        raise NotImplementedError
    
    def current_title(self):
        return self[self.current_index()][0]
    
    def current_widget(self):
        return self[self.current_index()][1]

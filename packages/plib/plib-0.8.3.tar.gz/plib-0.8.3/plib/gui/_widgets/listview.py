#!/usr/bin/env python
"""
Module LISTVIEW -- GUI Tree/List View Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for tree view/list view widgets.
"""

import sys
import new

from plib.gui.defs import *
from plib.gui._widgets import _control, _helpers, _signal


class PListViewItemCols(_helpers._PTreeHelperItemCols):
    """Exposes columns of a list view item as a sequence.
    """
    
    def _get_listviewitem(self):
        return self._helperitem
    
    listviewitem = property(_get_listviewitem)
    
    def _get_data(self, index):
        return self.listviewitem._get_col(index)
    
    def _set_data(self, index, value):
        self.listviewitem._set_col(index, value)


class PListViewItemBase(_helpers._PTreeHelperItem):
    """List view item that looks like a sequence of 2-tuples.
    
    Each 2-tuple in the sequence is of the form
    (column-values, [list of child items]). The column-values
    is a list of strings; if the list view has only one column,
    the list has a single element.
    """
    
    colsclass = PListViewItemCols
    
    def __init__(self, parent, index, data=None):
        self._parent = parent
        self._depth = 0
        self._listview = self._listview_from_parent(parent)
        _helpers._PTreeHelperItem.__init__(self, parent, index, data)
    
    def _listview_from_parent(self, p):
        while not isinstance(p, self.listviewclass):
            p = p._parent
            self._depth += 1
        return p
    
    def _get_listview(self):
        return self._listview
    
    listview = property(_get_listview)
    
    def colcount(self):
        return self.listview.colcount()
    
    def _get_col(self, col):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_col(self, col, value):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def expand(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PListViewLabelsBase(_helpers._PHelperColLabels):
    
    def _get_listview(self):
        return self._helper
    
    listview = property(_get_listview)


class PListViewMixin(_helpers._PTreeHelper):
    """Mixin class for PListViewBase and PListBoxBase.
    
    Implements common behaviors.
    
    Includes convenience methods to handle common special cases.
    """
    
    def __init__(self, parent, labels=None, data=None):
        # Some GUI toolkits define a clear method but it
        # doesn't work reliably, so we insist on using
        # ours (note that we have to create the bound
        # method by hand)
        self.clear = new.instancemethod(
            _helpers._PTreeHelper.clear, self, self.__class__)
        self._parent = parent
        if not hasattr(self.itemclass, 'listviewclass'):
            self.itemclass.listviewclass = self.__class__
        _helpers._PTreeHelper.__init__(self, labels, data)
    
    def colcount(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def extend_flat(self, items):
        """Adds list of multi-column items to list.
        
        Assumes no children, but multiple columns.
        """
        self.extend((item, []) for item in items)
    
    def extend_list(self, items):
        """Adds list of strings to list.
        
        Assumes a single column list box with no children.
        """
        self.extend(([item], []) for item in items)


class PListViewBase(_signal._PNotifyControl, PListViewMixin):
    """List view that looks like a list of child list view items.
    """
    
    signal = SIGNAL_LISTSELECTED
    
    def __init__(self, parent, labels=None, data=None, target=None):
        PListViewMixin.__init__(self, parent, labels, data)
        _signal._PNotifyControl.__init__(self, target)


class PListBoxBase(_control._PDialogControl, PListViewMixin):
    """List view specialized for use as a dialog control.
    """
    
    signal = SIGNAL_LISTSELECTED
    
    def __init__(self, parent, labels=None, data=None, target=None, geometry=None):
        PListViewMixin.__init__(self, parent, labels, data)
        _control._PDialogControl.__init__(self, target, geometry)

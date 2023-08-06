#!/usr/bin/env python
"""
Module WXLISTVIEW -- Python wxWidgets Tree/List View Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for the tree/list view widgets.
"""

import wx
from wx import gizmos

from plib.gui.defs import *
from plib.gui._widgets import listview

from _wxcommon import _PWxClientWidget, _PWxWidget, _wxalignmap


class _PWxListViewMixin(object):
    """Mixin class to help handle auto-sizing of columns.
    """
    
    def _get_autocols(self):
        if hasattr(self, '_autocols'):
            return self._autocols
        return self.listview.autocols
    
    autocols = property(_get_autocols)
    
    def AutoSizeItems(self, col):
        for item in self:
            item._size_col(col)
            item.AutoSizeItems(col)


class PWxListViewItem(_PWxListViewMixin, listview.PListViewItemBase):
    
    def __init__(self, parent, index, data=None):
        if index == len(parent):
            before = None
        else:
            before = parent._items[index]
        # Ugly hack to postpone creating the wx tree item until _set_col below
        self._b = before
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _helperdel(self, index, item):
        self.listview.Delete(item._id)
    
    def _get_col(self, col):
        return self.listview.GetItemText(self._id, col)
    
    def _set_col(self, col, value):
        value = str(value) # just in case
        if (col == 0) and not hasattr(self, '_id'):
            if self._b is not None:
                self._id = self.listview.InsertItem(
                    self._parent._id, self._b._id, value)
            else:
                self._id = self.listview.AppendItem(
                    self._parent._id, value)
            # this trick is to allow PWxListView.current_item to work
            self.listview.SetItemPyData(self._id, self)
            # ugly hack to clear up the instance namespace
            del self._b
        else:
            self.listview.SetItemText(self._id, value, col)
        self._size_col(col)
    
    def _size_col(self, col):
        if col in self.listview._autocols:
            self.listview.AutoSizeCol(col, self._get_col(col), self._depth)
    
    def expand(self):
        self.listview.Expand(self._id)


class PWxListViewLabels(listview.PListViewLabelsBase):
    
    def __init__(self, helper, labels=None):
        listview.PListViewLabelsBase.__init__(self, helper, labels)
        self.listview._id = self.listview.AddRoot("root")
    
    def _set_label(self, index, label):
        if (index == self.listview.colcount()):
            self.listview.AddColumn(label)
        else:
            self.listview.SetColumnText(index, label)
    
    def _set_width(self, index, width):
        self.listview.SetColumnWidth(index, width)
    
    def _set_align(self, index, align):
        # FIXME: this doesn't seem to work
        self.listview.SetColumnAlignment(index, _wxalignmap[align])
    
    def _set_readonly(self, index, readonly):
        pass


lv_style = wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT


class _PWxListViewBase(gizmos.TreeListCtrl, _PWxListViewMixin):
    
    itemclass = PWxListViewItem
    labelsclass = PWxListViewLabels
    
    _depth_w = 30 # additional column width for each sub-level in tree
    
    def __init__(self, parent):
        # This will be seen by the autocols property from mixin class above
        self._autocols = {}
        gizmos.TreeListCtrl.__init__(self, parent,
            style=lv_style)
        self._align = ALIGN_JUST # used by PWxPanel to determine placement
        self._expand = True
    
    def AutoSizeCol(self, col, newtext=None, newdepth=0):
        if newtext is None:
            newtext = self.GetColumnText(col)
        w = self.GetTextExtent(newtext)[0] + (newdepth * self._depth_w)
        if w > self.autocols[col]:
            self.autocols[col] = w
            gizmos.TreeListCtrl.SetColumnWidth(self, col, w)
    
    def AutoSizeCols(self, headeronly=False):
        for col in self.autocols:
            self.AutoSizeCol(col)
            if not headeronly:
                self.AutoSizeItems(col)
    
    def SetColumnWidth(self, index, width):
        # Override to handle auto resize for width -1
        if width > 0:
            if index in self.autocols:
                del self.autocols[index]
            gizmos.TreeListCtrl.SetColumnWidth(self, index, width)
        else:
            self.autocols[index] = self.GetColumnWidth(index)
            self.AutoSizeCol(index)
    
    def _helperdel(self, index, item):
        self.Delete(item._id)
    
    def _set_header_font_object(self, font_name, font_size, bold, italic):
        self.GetHeaderWindow().SetFont(self._wx_font_object(
            font_name, font_size, bold, italic))
        self.AutoSizeCols(True)
    
    def colcount(self):
        return self.GetColumnCount()
    
    def current_item(self):
        # the item pointer was stored in the wx tree item's PyData above
        return self.GetItemPyData(self.GetSelection())
    
    def set_current_item(self, item):
        self.SelectItem(item._id)


class PWxListView(_PWxListViewBase, _PWxClientWidget, listview.PListViewBase):
    
    def __init__(self, parent, labels=None, data=None, target=None):
        _PWxListViewBase.__init__(self, parent)
        listview.PListViewBase.__init__(self, parent, labels, data, target)
        if labels is not None:
            self.Expand(self._id)


class PWxListBox(_PWxListViewBase, _PWxWidget, listview.PListBoxBase):
    
    def __init__(self, parent, labels=None, data=None,
            target=None, geometry=None):
        
        _PWxListViewBase.__init__(self, parent)
        listview.PListBoxBase.__init__(self, parent, labels, data,
            target, geometry)
        if labels is not None:
            self.Expand(self._id)

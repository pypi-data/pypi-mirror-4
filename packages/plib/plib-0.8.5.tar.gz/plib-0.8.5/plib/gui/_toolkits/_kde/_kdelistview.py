#!/usr/bin/env python
"""
Module KDELISTVIEW -- Python KDE Tree/List View Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for the tree/list view widgets.
"""

import qt
import kdeui

from plib.gui._widgets import listview

from _kdecommon import (_PKDEMeta, _PKDEWidget, _PKDEClientWidget, _PKDECommunicator,
    _kdealignmap)


class _PKDEListViewMixin(object):
    """Mixin class for common behaviors of KDE list views and list view items.
    """
    
    def _helperdel(self, index, item):
        # Remove item from the parent list view or list view item
        self.takeItem(item)


class PKDEListViewItem(kdeui.KListViewItem,
        _PKDEListViewMixin, _PKDECommunicator,
        listview.PListViewItemBase):
    
    __metaclass__ = _PKDEMeta
    
    def __init__(self, parent, index, data=None):
        if index == 0:
            kdeui.KListViewItem.__init__(self, parent)
        else:
            after = parent._items[index - 1]
            kdeui.KListViewItem.__init__(self, parent, after)
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _get_col(self, col):
        return str(self.text(col))
    
    def _set_col(self, col, value):
        self.setText(col, str(value))
    
    def expand(self):
        self.setOpen(True)


class PKDEListViewLabels(listview.PListViewLabelsBase):
    
    def _set_label(self, index, label):
        if self.listview.columns() == index:
            self.listview.addColumn(str(label))
        else:
            self.listview.setColumnText(index, str(label))
    
    def _set_width(self, index, width):
        if width > 0:
            self.listview.setColumnWidthMode(index, qt.QListView.Manual)
            self.listview.setColumnWidth(index, width)
        elif width == -1:
            self.listview.setColumnWidthMode(index, qt.QListView.Maximum)
    
    def _set_align(self, index, align):
        # FIXME: wtf doesn't this align the column header as well?
        self.listview.setColumnAlignment(index, _kdealignmap[align])
    
    def _set_readonly(self, index, readonly):
        pass


class _PKDEListViewBase(kdeui.KListView, _PKDEListViewMixin):
    
    widget_class = kdeui.KListView
    
    itemclass = PKDEListViewItem
    labelsclass = PKDEListViewLabels
    
    def __init__(self, parent):
        kdeui.KListView.__init__(self, parent)
        self.setSorting(-1)
        self.setRootIsDecorated(True)
    
    def _set_header_font_object(self, font_name, font_size, bold, italic):
        self.header().setFont(self._qt_font_object(
            font_name, font_size, bold, italic))
    
    def colcount(self):
        return self.columns()
    
    def current_item(self):
        return self.currentItem()
    
    def set_current_item(self, item):
        self.setCurrentItem(item)


class PKDEListView(_PKDEListViewBase, _PKDEClientWidget,
        listview.PListViewBase):
    
    __metaclass__ = _PKDEMeta
    
    def __init__(self, parent, labels=None, data=None, target=None):
        _PKDEListViewBase.__init__(self, parent)
        listview.PListViewBase.__init__(self, parent, labels, data, target)


class PKDEListBox(_PKDEListViewBase, _PKDEWidget, listview.PListBoxBase):
    
    __metaclass__ = _PKDEMeta
    
    def __init__(self, parent, labels=None, data=None,
            target=None, geometry=None):
        
        _PKDEListViewBase.__init__(self, parent)
        listview.PListBoxBase.__init__(self, parent, labels, data,
            target, geometry)

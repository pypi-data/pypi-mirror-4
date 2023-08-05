#!/usr/bin/env python
"""
Module KDE4LISTVIEW -- Python KDE Tree/List View Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for the tree/list view widgets.
"""

# The KDE 4 "list view" is less flexible, so just use the Qt 4 widget
from PyQt4 import Qt as qt

from plib.gui._widgets import listview

from _kde4common import (_PKDEMeta, _PKDEWidget, _PKDEClientWidget, _PKDECommunicator,
     _kdealignmap)


class PKDEListViewItem(qt.QTreeWidgetItem, _PKDECommunicator,
        listview.PListViewItemBase):
    
    __metaclass__ = _PKDEMeta
    
    def __init__(self, parent, index, data=None):
        qt.QTreeWidgetItem.__init__(self, parent)
        parent._insert(self, index)
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _insert(self, item, index):
        if index == len(self):
            self.addChild(item)
        else:
            self.insertChild(index, item)
    
    def _helperdel(self, index, item):
        self.takeChild(index)
    
    def _get_col(self, col):
        return str(self.text(col))
    
    def _set_col(self, col, value):
        self.setText(col, str(value))
        # FIXME: it would be nice if this could be done once instead of
        # per item
        self.setTextAlignment(col,
            self.listview.headerItem().textAlignment(col))
    
    def expand(self):
        self.setExpanded(True)


class PKDEListViewLabels(listview.PListViewLabelsBase):
    
    label_list = None
    labels_initialized = False
    
    def _update(self, data):
        # Hack to get around weirdness in Qt 4 table widget API
        self.label_list = [str(value) for value in data]
        listview.PListViewLabelsBase._update(self, data)
    
    def _set_label(self, index, label):
        if self.label_list is not None:
            # First time setting labels, do it this way
            self.listview.setHeaderLabels(self.label_list)
            self.label_list = None
        if self.labels_initialized:
            # This allows labels to be changed after the initial setup
            item = self.listview.headerItem()
            item.setText(index, label)
        elif index == (len(self) - 1):
            # End of initial run
            self.labels_initialized = True
    
    def _set_width(self, index, width):
        if width > 0:
            self.listview.header().setResizeMode(index,
                qt.QHeaderView.Interactive)
            self.listview.header().resizeSection(index, width)
        else:
            self.listview.header().setResizeMode(index,
                qt.QHeaderView.ResizeToContents)
    
    def _set_align(self, index, align):
        item = self.listview.headerItem()
        item.setTextAlignment(index, _kdealignmap[align])
        # each item will align itself when added
    
    def _set_readonly(self, index, readonly):
        pass


class _PKDEListViewBase(qt.QTreeWidget):
    
    widget_class = qt.QTreeWidget
    
    itemclass = PKDEListViewItem
    labelsclass = PKDEListViewLabels
    
    def __init__(self, parent):
        qt.QTreeWidget.__init__(self, parent)
        self.header().setStretchLastSection(False)
        self.setSortingEnabled(False)
        self.setRootIsDecorated(True)
    
    def _insert(self, item, index):
        if index == len(self):
            self.addTopLevelItem(item)
        else:
            self.insertTopLevelItem(index, item)
    
    def _helperdel(self, index, item):
        self.takeTopLevelItem(index)
    
    def _set_header_font_object(self, font_name, font_size, bold, italic):
        self.header().setFont(self._qt_font_object(
            font_name, font_size, bold, italic))
    
    def colcount(self):
        return self.columnCount()
    
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


class PKDEListBox(_PKDEListViewBase, _PKDEWidget,
        listview.PListBoxBase):
    
    __metaclass__ = _PKDEMeta
    
    def __init__(self, parent, labels=None, data=None,
            target=None, geometry=None):
        
        _PKDEListViewBase.__init__(self, parent)
        listview.PListBoxBase.__init__(self, parent, labels, data,
            target, geometry)

#!/usr/bin/env python
"""
Module QTLISTVIEW -- Python Qt Tree/List View Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for the tree/list view widgets.
"""

import qt

from plib.gui._widgets import listview

from _qtcommon import (_PQtMeta, _PQtWidget, _PQtClientWidget, _PQtCommunicator,
    _qtalignmap)


class _PQtListViewMixin(object):
    # Mixin class to handle common behaviors of Qt list views
    # and list view items.
    
    def _helperdel(self, index, item):
        # Remove item from the parent list view or list view item
        self.takeItem(item)


class PQtListViewItem(qt.QListViewItem, _PQtCommunicator,
    _PQtListViewMixin, listview.PListViewItemBase):
    
    __metaclass__ = _PQtMeta
    
    def __init__(self, parent, index, data=None):
        if index == 0:
            qt.QListViewItem.__init__(self, parent)
        else:
            after = parent._items[index - 1]
            qt.QListViewItem.__init__(self, parent, after)
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _get_col(self, col):
        return str(self.text(col))
    
    def _set_col(self, col, value):
        self.setText(col, str(value))
    
    def expand(self):
        self.setOpen(True)


class PQtListViewLabels(listview.PListViewLabelsBase):
    
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
        self.listview.setColumnAlignment(index, _qtalignmap[align])
    
    def _set_readonly(self, index, readonly):
        pass


class _PQtListViewBase(qt.QListView, _PQtListViewMixin):
    
    widget_class = qt.QListView
    
    itemclass = PQtListViewItem
    labelsclass = PQtListViewLabels
    
    def __init__(self, parent):
        qt.QListView.__init__(self, parent)
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


class PQtListView(_PQtListViewBase, _PQtClientWidget,
        listview.PListViewBase):
    
    __metaclass__ = _PQtMeta
    
    def __init__(self, parent, labels=None, data=None, target=None):
        _PQtListViewBase.__init__(self, parent)
        listview.PListViewBase.__init__(self, parent, labels, data, target)


class PQtListBox(_PQtListViewBase, _PQtWidget,
        listview.PListBoxBase):
    
    __metaclass__ = _PQtMeta
    
    def __init__(self, parent, labels=None, data=None,
            target=None, geometry=None):
        _PQtListViewBase.__init__(self, parent)
        listview.PListBoxBase.__init__(self, parent, labels, data,
            target, geometry)

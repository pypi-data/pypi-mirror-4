#!/usr/bin/env python
"""
Module KDE4TABLE -- Python KDE Table Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for the table widgets.
"""

from PyQt4 import Qt as qt

from plib.gui._widgets import table

from _kde4common import _PKDEMeta, _PKDEClientWidget, _kdealignmap


class PKDETableLabels(table.PTableLabelsBase):
    
    label_list = None
    labels_initialized = False
    
    def _update(self, data):
        # Hack to get around weirdness in Qt 4 table widget API
        self.label_list = [str(value) for value in data]
        table.PTableLabelsBase._update(self, data)
    
    def _set_label(self, index, label):
        if self.label_list is not None:
            # First time setting labels, do it this way
            self.table.setHorizontalHeaderLabels(self.label_list)
            self.label_list = None
        if self.labels_initialized:
            # This allows labels to be changed after the initial setup
            item = self.table.horizontalHeaderItem(index)
            item.setText(label)
        elif index == (len(self) - 1):
            # End of initial run
            self.labels_initialized = True
    
    def _set_width(self, index, width):
        if width > 0:
            self.table.horizontalHeader().setResizeMode(index,
                qt.QHeaderView.Interactive)
            self.table.horizontalHeader().resizeSection(index, width)
        else:
            self.table.horizontalHeader().setResizeMode(index,
                qt.QHeaderView.ResizeToContents)
    
    def _set_align(self, index, align):
        self.table.horizontalHeaderItem(index).setTextAlignment(
            _kdealignmap[align])
        # Table cells will align themselves when added
    
    def _set_readonly(self, index, readonly):
        #self.table.setColumnReadOnly(index, readonly)
        pass


class PKDETable(qt.QTableWidget, _PKDEClientWidget, table.PTableBase):
    
    __metaclass__ = _PKDEMeta
    
    widget_class = qt.QTableWidget
    
    labelsclass = PKDETableLabels
    
    def __init__(self, parent, labels=None, data=None, target=None):
        qt.QTableWidget.__init__(self, parent)
        self.setSortingEnabled(False)
        # Used by ugly hack in default fg and bk color methods, below
        pal = self.palette()
        self._def_fgcolor = pal.color(self.foregroundRole())
        self._def_bkcolor = pal.color(self.backgroundRole())
        # Used by ugly hack in setup_notify, below
        self._setting_colors = False
        
        # This will initialize data (if any)
        table.PTableBase.__init__(self, parent, labels, data, target)
    
    def setup_notify(self, signal, target):
        # Hack to mask out table changed events fired when cell colors
        # are changed (the KDE 4 API says this shouldn't happen but it
        # does, go figure)
        if signal == self.signal:
            def _wrapper(row, col):
                if not self._setting_colors:
                    target(row, col)
            actual_target = _wrapper
        else:
            actual_target = target
        _PKDEClientWidget.setup_notify(self, signal, actual_target)
    
    def _get_item(self, row, col):
        result = self.item(row, col)
        if not isinstance(result, qt.QTableWidgetItem):
            result = qt.QTableWidgetItem()
            self.setItem(row, col, result)
        return result
    
    def _set_header_font_object(self, font_name, font_size, bold, italic):
        self.horizontalHeader().setFont(self._qt_font_object(
            font_name, font_size, bold, italic))
    
    def _get_cell(self, row, col):
        # Need str conversion here since widgets return QStrings
        return str(self._get_item(row, col).text())
    
    def _set_cell(self, row, col, value):
        item = self._get_item(row, col)
        item.setText(str(value))
        # FIXME: it would be nice if this could be done once instead of
        # per item
        item.setTextAlignment(self.horizontalHeaderItem(col).textAlignment())
    
    def rowcount(self):
        return self.rowCount()
    
    def colcount(self):
        return self.columnCount()
    
    def set_colcount(self, count):
        self.setColumnCount(count)
    
    def current_row(self):
        return self.currentRow()
    
    def current_col(self):
        return self.currentColumn()
    
    def _insert_row(self, index):
        self.insertRow(index)
    
    def _remove_row(self, index):
        self.removeRow(index)
    
    def set_min_size(self, width, height):
        self.setMinimumSize(width, height)
    
    def topmargin(self):
        return 0 #self.topMargin()
    
    def leftmargin(self):
        return 0 #self.leftMargin()
    
    def rowheight(self, row):
        return self.rowHeight(row)
    
    def colwidth(self, col):
        return self.columnWidth(col)
    
    def default_fgcolor(self):
        return self._def_fgcolor
    
    def default_bkcolor(self):
        return self._def_bkcolor
    
    def set_text_fgcolor(self, row, col, color):
        item = self._get_item(row, col)
        self._setting_colors = True
        item.setTextColor(self._mapped_color(color))
        self._setting_colors = False
    
    def set_cell_bkcolor(self, row, col, color):
        item = self._get_item(row, col)
        self._setting_colors = True
        item.setBackgroundColor(self._mapped_color(color))
        self._setting_colors = False

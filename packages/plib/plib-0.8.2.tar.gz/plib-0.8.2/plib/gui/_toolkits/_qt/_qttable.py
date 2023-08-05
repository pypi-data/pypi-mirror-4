#!/usr/bin/env python
"""
Module QTTABLE -- Python Qt Table Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for the table widgets.
"""

import qt
import qttable

from plib.gui._widgets import table

from _qtcommon import _PQtMeta, _PQtClientWidget


class PQtTableLabels(table.PTableLabelsBase):
    
    def _set_label(self, index, label):
        self.table.horizontalHeader().setLabel(index, label)
    
    def _set_width(self, index, width):
        self.table.horizontalHeader().resizeSection(index, width)
    
    def _set_align(self, index, align):
        # TODO: Add derived QTableItem class to allow column alignments
        # (Why the @#$&*! isn't that built into Qt?)
        pass
    
    def _set_readonly(self, index, readonly):
        self.table.setColumnReadOnly(index, readonly)


class PQtTable(qttable.QTable, _PQtClientWidget, table.PTableBase):
    
    __metaclass__ = _PQtMeta
    
    widget_class = qttable.QTable
    
    labelsclass = PQtTableLabels
    
    def __init__(self, parent, labels=None, data=None, target=None):
        qttable.QTable.__init__(self, parent)
        self.setSorting(False)
        
        # These will be needed to hack customized colors below
        self.textcolors = {}
        self.cellcolors = {}
        #self._painted = False
        
        # This will initialize data (if any)
        table.PTableBase.__init__(self, parent, labels, data, target)
    
    def _set_header_font_object(self, font_name, font_size, bold, italic):
        self.horizontalHeader().setFont(self._qt_font_object(
            font_name, font_size, bold, italic))
    
    def _get_cell(self, row, col):
        # Need str conversion here since widgets return QStrings
        return str(self.text(row, col))
    
    def _set_cell(self, row, col, value):
        self.setText(row, col, str(value))
    
    def rowcount(self):
        return self.numRows()
    
    def colcount(self):
        return self.numCols()
    
    def set_colcount(self, count):
        self.setNumCols(count)
    
    def current_row(self):
        return self.currentRow()
    
    def current_col(self):
        return self.currentColumn()
    
    def _insert_row(self, index):
        self.insertRows(index)
    
    def _remove_row(self, index):
        self.removeRow(index)
    
    def set_min_size(self, width, height):
        self.setMinimumSize(width, height)
    
    def topmargin(self):
        return self.topMargin()
    
    def leftmargin(self):
        return self.leftMargin()
    
    def rowheight(self, row):
        return self.rowHeight(row)
    
    def colwidth(self, col):
        return self.columnWidth(col)
    
    def default_fgcolor(self):
        return None
    
    def default_bkcolor(self):
        return None
    
    def _set_color(self, mapping, row, col, color):
        if color is None:
            if (row, col) in mapping:
                del mapping[(row, col)]
        else:
            mapping[(row, col)] = self._mapped_color(color)
    
    def set_text_fgcolor(self, row, col, color):
        self._set_color(self.textcolors, row, col, color)
    
    def set_cell_bkcolor(self, row, col, color):
        self._set_color(self.cellcolors, row, col, color)
    
    #def force_repaint(self):
    #    if self._painted:
    #        self.invalidate()
    #        self.erase()
    #        self.update()
    
    def paintCell(self, painter, row, col, rect, selected, colorgroup=None):
        """Override to allow customized text and background colors.
        """
        
        #if not self._painted:
        #    self._painted = True
        
        # FIXME: wtf isn't this already built into Qt???
        if colorgroup is not None:
            if (row, col) in self.textcolors:
                colorgroup.setColor(qt.QColorGroup.Text,
                    self.textcolors[(row, col)])
            if (row, col) in self.cellcolors:
                colorgroup.setColor(qt.QColorGroup.Base,
                    self.cellcolors[(row, col)])
            qttable.QTable.paintCell(self, painter, row, col, rect, selected,
                colorgroup)
        else:
            # FIXME: while we're venting, wtf is this block necessary?
            # (i.e., why can't we just make the above call with colorgroup
            # set to None?)
            qttable.QTable.paintCell(self, painter, row, col, rect, selected)

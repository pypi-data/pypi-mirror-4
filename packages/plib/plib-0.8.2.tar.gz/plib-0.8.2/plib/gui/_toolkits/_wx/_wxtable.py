#!/usr/bin/env python
"""
Module WXTABLE -- Python wxWidgets Table Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for table table.
"""

import wx.grid

from plib.gui.defs import *
from plib.gui._widgets import table

from _wxcommon import _PWxClientWidget, _wxalignmap


class PWxTableLabels(table.PTableLabelsBase):
    
    def _set_label(self, index, label):
        self.table.SetColLabelValue(index, label)
    
    def _set_width(self, index, width):
        self.table.SetColSize(index, width)
    
    def _set_align(self, index, align):
        pass
    
    def _set_readonly(self, index, readonly):
        pass


class PWxTable(wx.grid.Grid, _PWxClientWidget, table.PTableBase):
    
    labelsclass = PWxTableLabels
    
    def __init__(self, parent, labels=None, data=None, target=None):
        wx.grid.Grid.__init__(self, parent, -1)
        self._align = ALIGN_JUST # used by PWxPanel to determine placement
        self._expand = True
        self.CreateGrid(0, 0)
        table.PTableBase.__init__(self, parent, labels, data, target)
    
    def _set_header_font_object(self, font_name, font_size, bold, italic):
        self.SetLabelFont(self._wx_font_object(
            font_name, font_size, bold, italic))
    
    def _get_cell(self, row, col):
        return self.GetCellValue(row, col)
    
    def _set_cell(self, row, col, value):
        self.SetCellValue(row, col, value)
    
    def rowcount(self):
        return self.GetNumberRows()
    
    def colcount(self):
        return self.GetNumberCols()
    
    def set_colcount(self, count):
        self.InsertCols(0, count)
    
    def current_row(self):
        return self.GetGridCursorRow()
    
    def current_col(self):
        return self.GetGridCursorCol()
    
    def _insert_row(self, index):
        self.InsertRows(index, 1)
    
    def _remove_row(self, index):
        self.DeleteRows(index, 1)
    
    def set_min_size(self, width, height):
        self.SetSizeHints(width, height)
    
    def topmargin(self):
        return self.GetColLabelSize()
    
    def leftmargin(self):
        return self.GetRowLabelSize()
    
    def rowheight(self, row):
        return self.GetRowSize(row)
    
    def colwidth(self, col):
        return self.GetColSize(col)
    
    def default_fgcolor(self):
        return self.GetDefaultCellTextColour()
    
    def default_bkcolor(self):
        return self.GetDefaultCellBackgroundColour()
    
    def set_text_fgcolor(self, row, col, color):
        self.SetCellTextColour(row, col, color)
    
    def set_cell_bkcolor(self, row, col, color):
        self.SetCellBackgroundColour(row, col, color)

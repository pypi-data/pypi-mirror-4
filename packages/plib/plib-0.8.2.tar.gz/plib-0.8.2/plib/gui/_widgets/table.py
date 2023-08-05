#!/usr/bin/env python
"""
Module TABLE -- GUI Table Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for table widgets.
"""

import sys

from plib.gui.defs import *
from plib.gui._widgets import _helpers
from plib.gui._widgets import _signal

scrollbarsize = 20
gridlinesize = 2


class PTableRow(_helpers._PRowHelperItem):
    """Table row helper class.
    
    Looks like a list of strings (the values in the cells
    in this row).
    """
    
    def _get_table(self):
        return self._helper
    
    def _get_row(self):
        return self._i
    
    table = property(_get_table)
    row = property(_get_row)
    
    def __len__(self):
        return self.table.colcount()
    
    def _get_data(self, index):
        return self.table._get_cell(self._i, index)
    
    def _set_data(self, index, value):
        self.table._set_cell(self._i, index, value)


class PTableLabelsBase(_helpers._PHelperColLabels):
    """Table labels helper class.
    
    Note that the length of the list of labels passed to
    this class determines the column count of the table.
    """
    
    def _update(self, data):
        if self.table.colcount() != len(data):
            self.table.set_colcount(len(data))
        _helpers._PHelperColLabels._update(self, data)
    
    def _get_table(self):
        return self._helper
    
    table = property(_get_table)


class PTableBase(_signal._PNotifyControl, _helpers._PRowHelper):
    """Table class that looks like a list of PTableRows.
    
    Each PTableRow looks like a list of strings. Double-indexing
    the table by [row][col] therefore retrieves the string in
    cell row, col).
    """
    
    signal = SIGNAL_TABLECHANGED
    itemclass = PTableRow
    defaultcolwidth = 100
    defaultrowheight = 25
    defaultmargin = 25
    
    def __init__(self, parent, labels=None, data=None, target=None):
        self._parent = parent
        _signal._PNotifyControl.__init__(self, target)
        _helpers._PRowHelper.__init__(self, labels, data)
        
        # set minimum size after initializing data if there is data
        if data is not None:
            self.set_min_size(self.minwidth(), self.minheight())
    
    def _get_cell(self, row, col):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_cell(self, row, col, value):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def colcount(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_colcount(self, count):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def current_col(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def current_cell(self):
        r = self.current_row()
        c = self.current_col()
        if (r < 0) or (c < 0):
            return None
        else:
            return self.items[r][c]
    
    def set_min_size(self, width, height):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def topmargin(self):
        return self.defaultmargin
    
    def leftmargin(self):
        return self.defaultmargin
    
    def rowheight(self, row):
        return self.defaultrowheight
    
    def colwidth(self, col):
        return self.defaultcolwidth
    
    if sys.version_info < (2, 4):
        
        def minwidth(self):
            return sum([self.colwidth(col)
                    for col in xrange(self.colcount())]) + \
                self.leftmargin() + scrollbarsize + \
                (self.colcount() * gridlinesize)
        
        def minheight(self):
            return sum([self.rowheight(row)
                    for row in xrange(self.rowcount())]) + \
                self.topmargin() + scrollbarsize + \
                (self.rowcount() * gridlinesize)
    
    else:
        
        def minwidth(self):
            return sum(self.colwidth(col)
                    for col in xrange(self.colcount())) + \
                self.leftmargin() + scrollbarsize + \
                (self.colcount() * gridlinesize)
        
        def minheight(self):
            return sum(self.rowheight(row)
                    for row in xrange(self.rowcount())) + \
                self.topmargin() + scrollbarsize + \
                (self.rowcount() * gridlinesize)
    
    def force_repaint(self):
        """Placeholder for derived classes to implement.
        """
        pass
    
    def default_fgcolor(self):
        return COLOR_BLACK
    
    def default_bkcolor(self):
        return COLOR_WHITE
    
    def set_text_fgcolor(self, row, col, color):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_cell_bkcolor(self, row, col, color):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_row_fgcolor(self, row, color):
        for col in range(self.colcount()):
            self.set_text_fgcolor(row, col, color)
        self.force_repaint()
    
    def set_row_bkcolor(self, row, color):
        for col in range(self.colcount()):
            self.set_cell_bkcolor(row, col, color)
        self.force_repaint()
    
    def set_col_fgcolor(self, col, color):
        for row in range(self.rowcount()):
            self.set_text_fgcolor(row, col, color)
        self.force_repaint()
    
    def set_col_bkcolor(self, col, color):
        for row in range(self.rowcount()):
            self.set_cell_bkcolor(row, col, color)
        self.force_repaint()

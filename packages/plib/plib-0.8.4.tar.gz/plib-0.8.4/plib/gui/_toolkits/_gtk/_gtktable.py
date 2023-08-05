#!/usr/bin/env python
"""
Module GTKTABLE -- Python GTK Table Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI objects for the table widgets.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from plib.gui.defs import *
from plib.gui._widgets import table

from _gtkcommon import (_PGtkMeta, _PGtkClientWidget, _PGtkCommunicator,
    _gtkalignmap, _gtksignals)

table.gridlinesize += 2


class PGtkTableEntry(gtk.Entry, _PGtkCommunicator):
    """Cell entry widget that causes table to emit signal when changed.
    """
    
    def __init__(self, table, row, col):
        gtk.Entry.__init__(self)
        self._t = table
        self._r = row
        self._c = col
        self._initialized = False  # avoid index out of range on startup
        
        # The table cell signals get spotted here and forwarded
        self.connect("focus_in_event", self.cellselected)
        self.connect("changed", self.entrychanged)
    
    def cellselected(self, obj, event):
        self._t.do_notify(SIGNAL_CELLSELECTED, self._r, self._c)
    
    def entrychanged(self, obj):
        # FIXME: Figure out why this hack is necessary to avoid index out of
        # range on initial startup when the first changed event fires
        if self._initialized:
            self._t.do_notify(SIGNAL_TABLECHANGED, self._r, self._c)
        else:
            # First time setting the value, fire the event next time
            self._initialized = True


class PGtkTableFrame(gtk.Frame):
    """Frame to draw border around cell entry and label widgets.
    """
    
    shadow_type = gtk.SHADOW_NONE
    
    def __init__(self, widget):
        gtk.Frame.__init__(self)
        self._w = widget
        self.set_shadow_type(self.shadow_type)
        self.add(widget)
        widget.show()


class PGtkTableLabels(table.PTableLabelsBase):
    
    #def dodisplay(self):
    def _update(self, data):
        # TODO: Get rid of this hack or find a better place for it
        if len(self.table.widgets) == 0:
            self.table._attach_widget(0, 0, PGtkTableFrame(gtk.Label()))
        table.PTableLabelsBase._update(self, data)
    
    def _set_label(self, index, label):
        self.table._attach_widget(0, index + 1,
            PGtkTableFrame(gtk.Label(label)))
    
    def _set_width(self, index, width):
        pass
    
    def _set_align(self, index, align):
        pass
    
    def _set_readonly(self, index, readonly):
        pass


class PGtkTable(gtk.Table, _PGtkClientWidget, table.PTableBase):
    
    __metaclass__ = _PGtkMeta
    
    labelsclass = PGtkTableLabels
    
    # Define signals using 'automagic' class field
    __gsignals__ = {
        _gtksignals[SIGNAL_CELLSELECTED]:
            (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
            (gobject.TYPE_INT, gobject.TYPE_INT)),
        _gtksignals[SIGNAL_TABLECHANGED]:
            (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
            (gobject.TYPE_INT, gobject.TYPE_INT))
    }
    
    _align = ALIGN_JUST # used by PGtkPanel to determine expand/fill
    
    def __init__(self, parent, labels=None, data=None, target=None):
        """Expects labels to be a list of PLabels.
        """
        
        self._l = labels
        self._r = 0
        self._c = len(labels)
        self.widgets = {}
        self.rowlabels = {}
        gtk.Table.__init__(self, self._r + 1, self._c + 1)
        table.PTableBase.__init__(self, parent, labels, data, target)
    
    # We have to override gtk.Table's Python container methods since they
    # iterate over cells instead of rows
    
    def __len__(self):
        return table.PTableBase.__len__(self)
    
    def __iter__(self):
        return table.PTableBase.__iter__(self)
    
    def _attach_widget(self, r, c, widget=None):
        if widget is None:
            widget = self.widgets[(r - 1, c - 1)]
        widget.set_size_request(self.colwidth(c - 1), self.defaultrowheight)
        self.attach(widget, c, c + 1, r, r + 1, gtk.FILL, gtk.FILL)
        widget.show()
    
    def _fit_size(self):
        self.resize(self._r + 1, self._c + 1)
    
    def _set_header_font_object(self, font_name, font_size, bold, italic):
        #self._font_widget().modify_font(self._gtk_font_desc(font_name, font_size, bold, italic))
        pass
    
    def _get_cell(self, row, col):
        if (row, col) in self.widgets:
            return self.widgets[(row, col)]._w.get_text()
        else:
            return ""
    
    def _set_cell(self, row, col, value):
        if (row, col) not in self.widgets:
            self.widgets[(row, col)] = PGtkTableFrame(
                PGtkTableEntry(self, row, col))
            self._attach_widget(row + 1, col + 1)
        self.widgets[(row, col)]._w.set_text(value)
    
    def rowcount(self):
        return self._r
    
    def colcount(self):
        return self._c
    
    def set_colcount(self, count):
        # TODO: Add code here that can be called from table labels _update
        pass
    
    def current_row(self):
        return -1
    
    def current_col(self):
        return -1
    
    def _insert_row(self, index):
        self._r += 1
        self._fit_size()
        self.rowlabels[index] = PGtkTableFrame(gtk.Label(str(self._r)))
        self._attach_widget(self._r, 0, self.rowlabels[index])
    
    def _remove_row(self, index):
        if self._r > 0:
            for col in range(self.colcount()):
                if (index, col) in self.widgets:
                    self.remove(self.widgets[(index, col)])
                    del self.widgets[(index, col)]
            self.remove(self.rowlabels[index])
            del self.rowlabels[index]
            self._r -= 1
            self._fit_size()
    
    def set_min_size(self, width, height):
        self.set_size_request(width, height)
    
    def colwidth(self, col):
        if col < 0:
            return self.defaultmargin + table.gridlinesize
        else:
            return self._l[col].width + table.gridlinesize
    
    def set_text_fgcolor(self, row, col, color):
        pass # FIXME
    
    def set_cell_bkcolor(self, row, col, color):
        pass # FIXME

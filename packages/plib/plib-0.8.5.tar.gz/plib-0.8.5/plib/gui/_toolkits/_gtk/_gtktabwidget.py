#!/usr/bin/env python
"""
Module GTKTABWIDGET -- Python Gtk Tab Widget
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Gtk GUI objects for the tab widget.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from plib.gui.defs import *
from plib.gui._widgets import tabwidget

from _gtkcommon import _PGtkMeta, _PGtkClientWidget, _gtksignals


class PGtkTabWidget(gtk.Notebook, _PGtkClientWidget,
        tabwidget.PTabWidgetBase):
    
    __metaclass__ = _PGtkMeta
    
    # Define tab changed signal using 'automagic' class field
    __gsignals__ = { _gtksignals[SIGNAL_TABCHANGED]:
        (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)) }
    
    _align = ALIGN_JUST # used by PGtkPanel to determine expand/fill
    
    def __init__(self, parent, tabs=None, target=None):
        gtk.Notebook.__init__(self)
        tabwidget.PTabWidgetBase.__init__(self, parent, tabs, target)
        
        # The tab changed signal doesn't include a usable pointer to the
        # new widget, so gateway it
        self._initialized = False  # prevent firing an extra event on startup
        self.connect("switch_page", self.tab_switched)
    
    def tab_switched(self, obj, page, index):
        """New tab was selected.
        """
        if self._initialized:
            self.do_notify(SIGNAL_TABCHANGED, self._items[index])
        else:
            self._initialized = True
    
    def __len__(self):
        return self.get_n_pages()
    
    def _get_tabtitle(self, index):
        return self.get_tab_label_text(self._items[index])
    
    def _set_tabtitle(self, index, title):
        self.set_tab_label_text(self._items[index], title)
    
    def _add_tab(self, index, title, widget):
        if hasattr(widget, '_box'):
            widget = widget._box
        self.insert_page(widget, None, index)
        self.set_tab_label_text(widget, title)
        widget.show()
    
    def _del_tab(self, index):
        self.remove_page(index)
    
    def _add_widget(self, widget, x=0, y=0):
        pass
    
    def current_index(self):
        return self.get_current_page()
    
    def set_current_index(self, index):
        self.set_current_page(index)

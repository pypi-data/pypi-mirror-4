#!/usr/bin/env python
"""
Module GTKLISTVIEW -- Python GTK Tree/List View Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI objects for the tree/list view widgets.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from plib.gui.defs import *
from plib.gui._widgets import listview

from _gtkcommon import _PGtkMeta, _PGtkClientWidget, _PGtkWidget, _gtkalignmap, _gtksignals


class PGtkListViewItem(listview.PListViewItemBase):
    
    def __init__(self, parent, index, data=None):
        if index == len(parent):
            before = None
        else:
            before = parent._items[index]
        # Ugly hack since we have to postpone creating the
        # gtk tree iter until _set_col below
        self._b = before
        listview.PListViewItemBase.__init__(self, parent, index, data)
    
    def _helperdel(self, index, item):
        self.listview._model.remove(item._iter)
    
    def _get_col(self, col):
        return self.listview._model.get_value(self._iter, col)
    
    def _set_col(self, col, value):
        if (col == 0) and not hasattr(self, '_iter'):
            if self._b is not None:
                self._iter = self.listview._model.insert_before(
                    self._parent._iter, self._b._iter)
            else:
                self._iter = self.listview._model.append(self._parent._iter)
            # this trick will allow PGtkListView.current_item to work
            self.listview._model.set_value(self._iter,
                self.listview._objcol, self)
            # ugly hack to clear up instance namespace
            del self._b
        self.listview._model.set_value(self._iter, col, value)
    
    def expand(self):
        self.listview.expand_to_path(
            self.listview._model.get_path(self._iter))


class PGtkListViewLabels(listview.PListViewLabelsBase):
    
    def __init__(self, parent, labels):
        self._columns = []
        listview.PListViewLabelsBase.__init__(self, parent, labels)
    
    def _set_label(self, index, label):
        if index == len(self._columns):
            column = gtk.TreeViewColumn(
                label, gtk.CellRendererText(), text=index)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
            self.listview.append_column(column)
            self._columns.append(column)
        else:
            self._columns[index].set_title(label)
    
    def _set_width(self, index, width):
        col = self._columns[index]
        if width > 0:
            # FIXME: the last column doesn't respect fixed sizing
            col.set_min_width(width)
            col.set_max_width(width)
            col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            col.set_fixed_width(width)
        elif width == -1:
            col.set_min_width(-1)
            col.set_max_width(-1)
            self._columns[index].set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
    
    def _set_align(self, index, align):
        # FIXME: wtf does this only align the header?
        self._columns[index].set_alignment(_gtkalignmap[align])
    
    def _set_readonly(self, index, readonly):
        pass


class _PGtkListViewBase(gtk.TreeView):
    
    itemclass = PGtkListViewItem
    labelsclass = PGtkListViewLabels
    
    # Define list view changed signal using 'automagic' class field
    __gsignals__ = { _gtksignals[SIGNAL_LISTSELECTED]:
        (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)) }
    
    def __init__(self, count):
        args = [gobject.TYPE_PYOBJECT]
        if count:
            args = ([gobject.TYPE_STRING] * count) + args
        args = tuple(args)
        self._model = gtk.TreeStore(*args)
        self._iter = None  # easier logic for adding top level items
        self._objcol = count  # column to store Python self object ref
        gtk.TreeView.__init__(self, self._model)
    
    def cursor_changed(self, obj):
        """The list view selection cursor was changed.
        """
        self.do_notify(SIGNAL_LISTSELECTED, self.current_item())
    
    def __iter__(self):
        """Need to override gtk.TreeView's iter method.
        """
        return listview.PListViewBase.__iter__(self)
    
    def _helperdel(self, index, item):
        self._model.remove(item._iter)
    
    def _set_header_font_object(self, font_name, font_size, bold, italic):
        #self._font_widget().modify_font(self._gtk_font_desc(font_name, font_size, bold, italic))
        pass
    
    def colcount(self):
        return self._model.get_n_columns()
    
    def current_item(self):
        model, iter = self.get_selection().get_selected()
        assert model == self._model  # if this throws an exception then everything's fubar
        # the Python self pointer was stored in self._objcol above
        return model.get_value(iter, self._objcol)
    
    def set_current_item(self, item):
        self.get_selection().select_iter(item._iter)


class PGtkListView(_PGtkListViewBase, _PGtkClientWidget,
        listview.PListViewBase):
    
    __metaclass__ = _PGtkMeta
    
    _align = ALIGN_JUST # used by PGtkPanel to determine expand/fill
    
    def __init__(self, parent, labels=None, data=None,
            target=None):
        
        if labels:
            count = len(labels)
        else:
            count = 0
        _PGtkListViewBase.__init__(self, count)
        # no __init__ method for _PGtkClientWidget
        listview.PListViewBase.__init__(self, parent, labels, data, target)
        
        # The list view changed signal doesn't contain the current item,
        # so gateway it
        self.connect("cursor_changed", self.cursor_changed)
    
    def __len__(self):
        """Need to override gtk.TreeView's len method.
        """
        return listview.PListViewBase.__len__(self)


class PGtkListBox(_PGtkListViewBase, _PGtkWidget,
        listview.PListBoxBase):
    
    __metaclass__ = _PGtkMeta
    
    def __init__(self, parent, labels=None, data=None,
            target=None, geometry=None):
        
        if labels:
            count = len(labels)
        else:
            count = 0
        _PGtkListViewBase.__init__(self, count)
        # FIXME: parent is set twice here and next line
        _PGtkWidget.__init__(self, parent, ALIGN_JUST)
        listview.PListBoxBase.__init__(self, parent, labels, data,
            target, geometry)
        
        # The list view changed signal doesn't contain the current item,
        # so gateway it
        self.connect("cursor_changed", self.cursor_changed)
    
    def __len__(self):
        """Need to override gtk.TreeView's len method.
        """
        return listview.PListBoxBase.__len__(self)

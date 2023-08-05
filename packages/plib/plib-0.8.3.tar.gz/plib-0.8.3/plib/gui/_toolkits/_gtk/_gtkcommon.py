#!/usr/bin/env python
"""
Module GTKCOMMON -- Python GTK Common Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK common GUI objects.
"""

from abc import ABCMeta

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import pango

from plib.gui.defs import *

_gtkalignmap = {
    ALIGN_LEFT: 0.0,
    ALIGN_CENTER: 0.5,
    ALIGN_RIGHT: 1.0 }

_gtkstockids = {
    ACTION_FILENEW: gtk.STOCK_NEW,
    ACTION_FILEOPEN: gtk.STOCK_OPEN,
    ACTION_FILESAVE: gtk.STOCK_SAVE,
    ACTION_FILESAVEAS: gtk.STOCK_SAVE_AS,
    ACTION_FILECLOSE: gtk.STOCK_CLOSE,
    ACTION_EDIT: gtk.STOCK_EDIT,
    ACTION_EDITUNDO: gtk.STOCK_UNDO,
    ACTION_EDITREDO: gtk.STOCK_REDO,
    ACTION_EDITCUT: gtk.STOCK_CUT,
    ACTION_EDITCOPY: gtk.STOCK_COPY,
    ACTION_EDITPASTE: gtk.STOCK_PASTE,
    ACTION_EDITDELETE: gtk.STOCK_DELETE,
    ACTION_REFRESH: gtk.STOCK_REFRESH,
    ACTION_ADD: gtk.STOCK_ADD,
    ACTION_REMOVE: gtk.STOCK_REMOVE,
    ACTION_APPLY: gtk.STOCK_APPLY,
    ACTION_OK: gtk.STOCK_OK,
    ACTION_CANCEL: gtk.STOCK_CANCEL,
    ACTION_PREFS: gtk.STOCK_PREFERENCES,
    ACTION_ABOUT: gtk.STOCK_ABOUT,
    ACTION_EXIT: gtk.STOCK_QUIT }

# Need this because earlier GTK versions lack this stock id
if hasattr(gtk, 'STOCK_SELECT_ALL'):
    _gtkstockids[ACTION_EDITSELECTALL] = gtk.STOCK_SELECT_ALL

_gtkicons = {
    MBOX_INFO: gtk.MESSAGE_INFO,
    MBOX_WARN: gtk.MESSAGE_WARNING,
    MBOX_ERROR: gtk.MESSAGE_ERROR,
    MBOX_QUERY: gtk.MESSAGE_QUESTION }

_stockidmap = {
    gtk.RESPONSE_YES: gtk.STOCK_YES,
    gtk.RESPONSE_NO: gtk.STOCK_NO,
    gtk.RESPONSE_CANCEL: gtk.STOCK_CANCEL,
    gtk.RESPONSE_OK: gtk.STOCK_OK }

_gtksignals = {
    SIGNAL_ACTIVATED: "activate",
    SIGNAL_CLICKED: "clicked",
    SIGNAL_TOGGLED: "toggled",
    SIGNAL_SELECTED: "selected",
    SIGNAL_FOCUS_IN: "focus_in_event",
    SIGNAL_FOCUS_OUT: "focus_out_event",
    SIGNAL_LISTSELECTED: "listview_changed",
    SIGNAL_CELLSELECTED: "table_cell_selected",
    SIGNAL_TABLECHANGED: "table_changed",
    SIGNAL_TEXTCHANGED: "text_changed",
    SIGNAL_TEXTSTATECHANGED: "textstate_changed", # FIXME: need mechanism to fire this signal
    SIGNAL_EDITCHANGED: "changed",
    SIGNAL_ENTER: "enter_pressed",
    SIGNAL_TABCHANGED: "tab_changed",
    SIGNAL_WIDGETCHANGED: "changed",
    SIGNAL_CLOSING: "window_closing",
    SIGNAL_HIDDEN: "destroy",
    SIGNAL_QUERYCLOSE: "delete_event",
    SIGNAL_BEFOREQUIT: "destroy" }

#_gtkfontfamilies = {
#    "Courier New": 'monospace',
#    "Times New Roman": 'serif',
#    "Arial": 'sans' }

# 'Wrapper' functions for certain signals to discard object parameter
# (since the way we're set up it will always be the same as self anyway)

_gtkwrappers = [
    SIGNAL_ACTIVATED, SIGNAL_CLICKED, SIGNAL_TOGGLED,
    SIGNAL_SELECTED, SIGNAL_LISTSELECTED,
    SIGNAL_CELLSELECTED, SIGNAL_TABLECHANGED,
    SIGNAL_TEXTCHANGED, SIGNAL_TEXTSTATECHANGED,
    SIGNAL_EDITCHANGED, SIGNAL_ENTER,
    SIGNAL_TABCHANGED]

_gtkplain = [SIGNAL_FOCUS_IN, SIGNAL_FOCUS_OUT,
    SIGNAL_QUERYCLOSE, SIGNAL_CLOSING,
    SIGNAL_HIDDEN, SIGNAL_BEFOREQUIT]


def _gtk_wrapper(target, plain=False):
    if plain:
        def wrapper(*args):
            target()
    else:
        def wrapper(obj, *args):
            target(*args)
    return wrapper


# Ugly hack to fix metaclass conflict for classes that use the collection
# ABCs

class _PGtkMeta(ABCMeta, gobject.GObjectMeta):
    
    def __init__(cls, name, bases, attrs):
        gobject.GObjectMeta.__init__(cls, name, bases, attrs)
        ABCMeta.__init__(cls, name, bases, attrs)


class _PGtkCommunicator(object):
    """Mixin class to abstract signal functionality in GTK.
    """
    
    def setup_notify(self, signal, target, wrap=True):
        if signal in _gtksignals:
            event = _gtksignals[signal]
            if wrap and (signal in _gtkwrappers):
                handler = _gtk_wrapper(target)
            elif signal in _gtkplain:
                handler = _gtk_wrapper(target, True)
            else:
                handler = target
            self.connect(event, handler)
    
    def do_notify(self, signal, *args):
        self.emit(_gtksignals[signal], *args)


_gtk_font_weights = [pango.WEIGHT_NORMAL, pango.WEIGHT_BOLD]
_gtk_font_styles = [pango.STYLE_NORMAL, pango.STYLE_ITALIC]


class _PGtkWidgetBase(object):
    """Mixin class to provide basic GTK widget methods.
    """
    
    fn_enable_get = 'get_sensitive'
    fn_enable_set = 'set_sensitive'
    
    def _widget(self):
        return self
    
    def update_widget(self):
        self._widget().queue_draw()
    
    def preferred_width(self):
        return self._widget().size_request()[0]
    
    def preferred_height(self):
        return self._widget().size_request()[1]
    
    def set_width(self, width):
        height = self._widget().get_size_request()[1]
        self._widget().set_size_request(width, height)
    
    def set_height(self, height):
        width = self._widget().get_size_request()[0]
        self._widget().set_size_request(width, height)
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self._parent._move_widget(self._widget(), left, top)
    
    def set_foreground_color(self, color):
        pass # FIXME
    
    def set_background_color(self, color):
        pass # FIXME
    
    def _font_widget(self):
        # Some Gtk widgets, like buttons, actually are containers and a child
        # widget is the one we need to set the font on; hence this method is
        # factored out
        return self
    
    # Chained method calls make it hard to meet PEP 8 80 chars per line...
    
    def get_font_name(self):
        return self._font_widget().get_pango_context().get_font_description().get_family()
    
    def get_font_size(self):
        return (self._font_widget().get_pango_context().get_font_description().get_size() / pango.SCALE)
    
    def get_font_bold(self):
        return (self._font_widget().get_pango_context().get_font_description().get_weight()
            == _gtk_font_weights[1])
    
    def get_font_italic(self):
        return (self._font_widget().get_pango_context().get_font_description().get_style()
            == _gtk_font_styles[1])
    
    def _gtk_font_desc(self, font_name, font_size, bold, italic):
        styles = []
        if bold:
            styles.append("bold")
        if italic:
            styles.append("italic")
        return pango.FontDescription("%s %s %s" %
            (font_name, " ".join(styles), font_size))
    
    def _set_font_object(self, font_name, font_size, bold, italic):
        self._font_widget().modify_font(self._gtk_font_desc(
            font_name, font_size, bold, italic))
    
    def set_focus(self):
        self._widget().grab_focus()


class _PGtkWidget_(_PGtkCommunicator, _PGtkWidgetBase):
    # Intermediate class so _PGtkClientWidget doesn't inherit the
    # overridden __init__ method
    pass


class _PGtkWidget(_PGtkWidget_):
    """Mixin class for GTK widgets that can send/receive signals.
    """
    
    def __init__(self, parent, align=ALIGN_LEFT):
        self._parent = parent
        self._align = align
        parent._add_widget(self)


class _PGtkClientWidget(_PGtkWidget_):
    """Mixin class for GTK main window client widgets.
    """
    pass

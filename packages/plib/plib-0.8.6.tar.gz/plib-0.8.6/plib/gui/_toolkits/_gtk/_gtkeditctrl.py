#!/usr/bin/env python
"""
Module GTKEDITCTRL -- Python GTK Editing Widgets
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI objects for edit controls.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from plib.gui._widgets import editctrl
from plib.gui.defs import *

from _gtkcommon import _PGtkWidget, _PGtkClientWidget, _gtksignals


class _PGtkEditMixin(object):
    
    fn_get_readonly = 'get_not_editable'
    fn_set_readonly = 'set_not_editable'
    
    def get_not_editable(self):
        return not self._edit.get_editable()
    
    def set_not_editable(self, value):
        self._edit.set_editable(not value)


class PGtkEditBox(gtk.Entry, _PGtkWidget, _PGtkEditMixin,
        editctrl.PEditBoxBase):
    
    fn_get_text = 'get_text'
    fn_set_text = 'set_text'
    
    # Need to define the 'enter' signal for Entry
    __gsignals__ = {
        _gtksignals[SIGNAL_ENTER]:
            (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        self._edit = self
        gtk.Entry.__init__(self)
        if expand:
            align = ALIGN_JUST
        else:
            align = ALIGN_LEFT
        _PGtkWidget.__init__(self, parent, align)
        # Connect to key pressed signal to catch Enter key
        self.connect("key_press_event", self.keypressed)
        editctrl.PEditBoxBase.__init__(self, target, geometry)
    
    def keypressed(self, widget, event):
        if event.keyval == gtk.keysyms.Return:
            self.do_notify(SIGNAL_ENTER)
            return True
        return False


class PGtkEditControl(gtk.ScrolledWindow,
        _PGtkClientWidget, _PGtkEditMixin,
        editctrl.PEditControlBase):
    
    fn_get_text = 'get_buffer_text'
    fn_set_text = 'set_buffer_text'
    
    # Need to define the 'changed' signal for TextView so it can pass it on
    __gsignals__ = {
        _gtksignals[SIGNAL_TEXTCHANGED]: (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        _gtksignals[SIGNAL_TEXTSTATECHANGED]: (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }
    
    _align = ALIGN_JUST # used by PGtkPanel to determine expand/fill
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        _PGtkWidget.__init__(self, parent, ALIGN_JUST)
        self._edit = gtk.TextView()
        self._clipboard = gtk.clipboard_get()
        if scrolling:
            self._edit.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self._edit.set_wrap_mode(gtk.WRAP_WORD)
        self._edit.get_buffer().connect("changed", self.textchanged)
        editctrl.PEditControlBase.__init__(self, target, geometry)
        self.add(self._edit)
        self._edit.show()
    
    def _font_widget(self):
        return self._edit
    
    def textchanged(self, buf):
        if buf is self._edit.get_buffer():
            # Pass on text buffer changed signal
            self.do_notify(SIGNAL_TEXTCHANGED)
    
    def get_buffer_text(self):
        buf = self._edit.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter())
    
    def set_buffer_text(self, value):
        self._edit.get_buffer().set_text(value)
    
    # FIXME: mechanism to fire this signal?
    def textstatechanged(self):
        self.do_notify(SIGNAL_TEXTSTATECHANGED)
    
    def can_undo(self):
        return False # FIXME
    
    def can_redo(self):
        return False # FIXME
    
    def can_clip(self):
        buf = self._edit.get_buffer()
        try:
            return buf.get_has_selection()
        except AttributeError:
            return True # FIXME
    
    def can_paste(self):
        return True # FIXME
    
    def undo_last(self):
        pass # FIXME
    
    def redo_last(self):
        pass # FIXME
    
    def select_all(self):
        pass # FIXME
    
    def delete_selected(self):
        self._edit.get_buffer().delete_selection(True,
            self._edit.get_editable())
    
    def copy_to_clipboard(self):
        self._edit.get_buffer().copy_clipboard(self._clipboard)
    
    def cut_to_clipboard(self):
        self._edit.get_buffer().cut_clipboard(self._clipboard,
            self._edit.get_editable())
    
    def paste_from_clipboard(self):
        self._edit.get_buffer().paste_clipboard(self._clipboard, None,
            self._edit.get_editable())

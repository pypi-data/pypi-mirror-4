#!/usr/bin/env python
"""
Module GTKDISPLAY -- Python GTK Text Display Widgets
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI objects for text display widgets.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from plib.gui._widgets import display
from plib.gui.defs import *

from _gtkcommon import _PGtkWidget


class PGtkTextDisplay(gtk.ScrolledWindow, _PGtkWidget,
        display.PTextDisplayBase):
    
    def __init__(self, parent, text=None, geometry=None, scrolling=False):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        _PGtkWidget.__init__(self, parent, ALIGN_JUST)
        self._edit = gtk.TextView()
        self._edit.set_editable(False)
        self._edit.set_cursor_visible(False)
        if scrolling:
            self._edit.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self._edit.set_wrap_mode(gtk.WRAP_WORD)
        display.PTextDisplayBase.__init__(self, text, geometry)
        self.add(self._edit)
        self._edit.show()
    
    def _font_widget(self):
        return self._edit
    
    def get_text(self):
        buf = self._edit.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter())
    
    def set_text(self, value):
        self._edit.get_buffer().set_text(value)

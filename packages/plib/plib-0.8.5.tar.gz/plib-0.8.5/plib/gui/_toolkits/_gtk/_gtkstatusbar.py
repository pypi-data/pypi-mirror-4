#!/usr/bin/env python
"""
Module GTKSTATUSBAR -- Python Gtk Status Bar Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Gtk GUI objects for the status bar.
"""

import pygtk
pygtk.require('2.0')
import gtk

from plib.gui._base import statusbar

from _gtkcommon import _PGtkWidgetBase
#from _gtklabel import PGtkTextLabel


class PGtkStatusBar(gtk.Statusbar, _PGtkWidgetBase, statusbar.PStatusBarBase):
    
    #textareaclass = PWxTextLabel # FIXME: not needed for gtk?
    
    def __init__(self, parent, widgets=None):
        gtk.Statusbar.__init__(self)
        statusbar.PStatusBarBase.__init__(self, parent, widgets)
    
    def _add_widget(self, widget, expand=False, custom=True):
        # FIXME: No custom widgets in gtk?
        pass
    
    def get_text(self):
        return "" # FIXME: no way to retrieve the status text in gtk?
    
    def set_text(self, value):
        self.push(self.get_context_id(value), value)

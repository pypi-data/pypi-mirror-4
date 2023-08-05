#!/usr/bin/env python
"""
Module GTKGROUPBOX -- Python Gtk Group Box Widgets
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Gtk GUI objects for group box widgets.
"""

import pygtk
pygtk.require('2.0')
import gtk

from plib.gui._widgets import groupbox
from plib.gui.defs import *

from _gtkcommon import _PGtkWidget


class PGtkGroupBox(gtk.Frame, _PGtkWidget, groupbox.PGroupBoxBase):
    
    def __init__(self, parent, caption, controls=None,
            margin=-1, spacing=-1, geometry=None):
        
        gtk.Frame.__init__(self)
        self._vbox = gtk.VBox()
        _PGtkWidget.__init__(self, parent, ALIGN_JUST)
        groupbox.PGroupBoxBase.__init__(self, parent, caption, controls,
            margin, spacing, geometry)
        self.add(self._vbox)
        self._vbox.show()
    
    def set_caption(self, caption):
        self.set_label(caption)
    
    def set_margin(self, margin):
        self._vbox.set_border_width(margin)
    
    def set_spacing(self, spacing):
        self._vbox.set_spacing(spacing)
    
    def _add_control(self, control):
        if hasattr(control, '_box'):
            control = control._box
        self._vbox.pack_start(control, False, False)
        control.show()

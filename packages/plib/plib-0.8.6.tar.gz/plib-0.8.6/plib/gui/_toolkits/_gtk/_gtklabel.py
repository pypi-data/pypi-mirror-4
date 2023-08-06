#!/usr/bin/env python
"""
Module GTKLABEL -- Python Gtk Text Label Widgets
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Gtk GUI objects for text label widgets.
"""

import pygtk
pygtk.require('2.0')
import gtk

from plib.gui._widgets import label

from _gtkcommon import _PGtkWidget


class PGtkTextLabel(gtk.Label, _PGtkWidget, label.PTextLabelBase):
    
    def __init__(self, parent, text=None, geometry=None):
        gtk.Label.__init__(self)
        self.set_alignment(0, 0.5)
        self.set_justify(gtk.JUSTIFY_LEFT)
        _PGtkWidget.__init__(self, parent)
        label.PTextLabelBase.__init__(self, text, geometry)
    
    # gtk.Label already has get_text and set_text methods, so they will
    # appear before the templates in label.PTextLabelBasein the MRO.
    # NOTE: This only works because gtk implements the methods as actual
    # method objects; it would *not* work in Qt, for example, because Qt
    # uses SWIG, which implements the methods as built-in functions, and
    # those will not show up in the MRO search.

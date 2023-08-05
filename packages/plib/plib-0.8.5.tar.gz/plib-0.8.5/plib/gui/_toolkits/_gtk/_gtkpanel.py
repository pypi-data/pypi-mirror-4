#!/usr/bin/env python
"""
Module GTKPANEL -- Python GTK Panel Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI objects for the panel widgets.
"""

import pygtk
pygtk.require('2.0')
import gtk

from plib.gui.defs import *
from plib.gui._widgets import panel

from _gtkcommon import _PGtkWidgetBase

_gtklayouts = {
    LAYOUT_NONE: gtk.HBox,
    LAYOUT_HORIZONTAL: gtk.HBox,
    LAYOUT_VERTICAL: gtk.VBox }


class PGtkPanel(_PGtkWidgetBase, panel.PPanelBase):
    
    def __init__(self, parent,
            layout=LAYOUT_NONE, style=PANEL_NONE, align=ALIGN_JUST,
            margin=-1, spacing=-1, width=-1, height=-1):
        
        try:
            self._box = _gtklayouts[layout]()
        except KeyError:
            self._box = None
        panel.PPanelBase.__init__(self, parent, layout, style, align,
            margin, spacing, width, height)
    
    def _widget(self):
        return self._box
    
    def _add_widget(self, widget, x=0, y=0):
        #FIXME: find better general method for widget adds
        pass
    
    def _move_widget(self, widget, x, y):
        #FIXME: implement moving sub-widgets?
        pass
    
    def _addwidget(self, widget):
        #FIXME: find better general method for widget adds
        exp = hasattr(widget, '_align') and (widget._align == ALIGN_JUST)
        if isinstance(widget, PGtkPanel):
            widget = widget._box
        #if hasattr(widget, '_adjust') and widget._adjust:
        #    bw, bh = widget.size_request()
        #    pw, ph = self._box.size_request()
        #    b = self._box.get_border_width()
        #    pw = pw - b
        #    ph = ph - b
        #    if (self._layout == LAYOUT_VERTICAL) and (pw > bw):
        #        widget.set_border_width((pw - bw)/2)
        #    elif (self._layout == LAYOUT_HORIZONTAL) and (ph > bh):
        #        widget.set_border_width((ph - bh)/2)
        self._box.pack_start(widget, expand=exp, fill=exp)
        widget.show()
    
    def _dolayout(self):
        self._box.show()
    
    def set_min_size(self, width, height):
        self._box.set_size_request(width, height)
    
    def set_box_width(self, width):
        pass # FIXME
    
    def set_margin(self, margin):
        self._box.set_border_width(margin)
    
    def set_spacing(self, spacing):
        self._box.set_spacing(spacing)

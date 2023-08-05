#!/usr/bin/env python
"""
Module KDE4LABEL -- Python KDE Text Label Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for text label widgets.
"""

#import kdeui # no obvious analog to plain QLabel in KDE
from PyQt4 import Qt as qt

from plib.gui._widgets import label

from _kde4common import _PKDEWidget


class PKDETextLabel(qt.QLabel, _PKDEWidget, label.PTextLabelBase):
    
    widget_class = qt.QLabel
    
    def __init__(self, parent, text=None, geometry=None):
        qt.QLabel.__init__(self, parent)
        label.PTextLabelBase.__init__(self, text, geometry)
    
    def get_text(self):
        return str(self.text())
    
    def set_text(self, value):
        self.setText(value)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # KDE text labels don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)

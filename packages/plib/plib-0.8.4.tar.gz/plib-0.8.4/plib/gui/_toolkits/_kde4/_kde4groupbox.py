#!/usr/bin/env python
"""
Module KDE4GROUPBOX -- Python KDE Group Box Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for group box widgets.
"""

#import kdeui # no obvious analog to plain QVGroupBox in KDE
from PyQt4 import Qt as qt

from plib.gui._widgets import groupbox

from _kde4common import _PKDEWidget


class PKDEGroupBox(qt.QGroupBox, _PKDEWidget, groupbox.PGroupBoxBase):
    
    widget_class = qt.QGroupBox
    
    def __init__(self, parent, caption, controls=None,
            margin=-1, spacing=-1, geometry=None):
        
        qt.QGroupBox.__init__(self, parent)
        self.setSizePolicy(
            qt.QSizePolicy.MinimumExpanding,
            qt.QSizePolicy.Fixed)
        self._vlayout = qt.QVBoxLayout()
        groupbox.PGroupBoxBase.__init__(self, parent, caption, controls,
            margin, spacing, geometry)
    
    def set_caption(self, caption):
        self.setTitle(caption)
    
    def set_margin(self, margin):
        self._vlayout.setContentsMargins(margin, margin, margin, margin)
    
    def set_spacing(self, spacing):
        self._vlayout.setSpacing(spacing)
    
    def _add_control(self, control):
        self._vlayout.addWidget(control)
    
    def _dolayout(self):
        self._vlayout.addStretch(1)
        self.setLayout(self._vlayout)

#!/usr/bin/env python
"""
Module QTGROUPBOX -- Python Qt Group Box Widgets
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for group box widgets.
"""

import qt

from plib.gui._widgets import groupbox

from _qtcommon import _PQtWidget


class PQtGroupBox(qt.QVGroupBox, _PQtWidget, groupbox.PGroupBoxBase):
    
    widget_class = qt.QVGroupBox
    
    def __init__(self, parent, caption, controls=None,
            margin=-1, spacing=-1, geometry=None):
        
        qt.QVGroupBox.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding,
            qt.QSizePolicy.Fixed)
        groupbox.PGroupBoxBase.__init__(self, parent, caption, controls,
            margin, spacing, geometry)
    
    def set_caption(self, caption):
        self.setTitle(caption)
    
    def set_margin(self, margin):
        self.setInsideMargin(margin)
    
    def set_spacing(self, spacing):
        self.setInsideSpacing(spacing)
    
    def _add_control(self, control):
        pass # parenting the control to the group box is enough in Qt

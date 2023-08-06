#!/usr/bin/env python
"""
Module QTPANEL -- Python Qt Panel Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for the panel widgets.
"""

import qt

from plib.gui.defs import *

from plib.gui._widgets import panel

from _qtcommon import _PQtWidgetBase

_qtpanels = {
    PANEL_NONE: qt.QFrame.NoFrame | qt.QFrame.Plain,
    PANEL_BOX: qt.QFrame.Box | qt.QFrame.Plain,
    PANEL_RAISED: qt.QFrame.Panel | qt.QFrame.Raised,
    PANEL_SUNKEN: qt.QFrame.Panel | qt.QFrame.Sunken }


def _qtsizepolicy(align):
    horiz = vert = qt.QSizePolicy.MinimumExpanding
    if align in (ALIGN_LEFT, ALIGN_RIGHT):
        horiz = qt.QSizePolicy.Fixed
    elif align in (ALIGN_TOP, ALIGN_BOTTOM):
        vert = qt.QSizePolicy.Fixed
    return horiz, vert


class PQtPanel(qt.QHBox, _PQtWidgetBase, panel.PPanelBase):
    
    def __init__(self, parent,
            layout=LAYOUT_NONE, style=PANEL_NONE, align=ALIGN_JUST,
            margin=-1, spacing=-1, width=-1, height=-1):
        
        qt.QHBox.__init__(self, (layout != LAYOUT_VERTICAL), parent,
            "unnamed")  # pick an arbitrary name, never used
        self.setFrameStyle(_qtpanels[style])
        self.setSizePolicy(*_qtsizepolicy(align))
        panel.PPanelBase.__init__(self, parent, layout, style, align,
            margin, spacing, width, height)
    
    def set_min_size(self, width, height):
        if width > -1:
            self.setMinimumWidth(width)
        if height > -1:
            self.setMinimumHeight(height)
    
    def set_box_width(self, width):
        self.setLineWidth(width)
    
    def set_margin(self, margin):
        self.setMargin(margin)
    
    def set_spacing(self, spacing):
        self.setSpacing(spacing)

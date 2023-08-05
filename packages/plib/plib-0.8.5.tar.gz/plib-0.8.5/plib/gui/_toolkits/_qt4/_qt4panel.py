#!/usr/bin/env python
"""
Module QT4PANEL -- Python Qt 4 Panel Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI objects for the panel widgets.
"""

try:
    from PySide import QtGui as qt
except ImportError:
    from PyQt4 import Qt as qt

from plib.gui.defs import *

from plib.gui._widgets import panel

from _qt4common import _PQtWidgetBase

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


class PQtPanel(qt.QFrame, _PQtWidgetBase, panel.PPanelBase):
    
    def __init__(self, parent,
            layout=LAYOUT_NONE, style=PANEL_NONE, align=ALIGN_JUST,
            margin=-1, spacing=-1, width=-1, height=-1):
        
        qt.QFrame.__init__(self, parent)
        self.setFrameStyle(_qtpanels[style])
        self.setSizePolicy(*_qtsizepolicy(align))
        if layout == LAYOUT_HORIZONTAL:
            klass = qt.QHBoxLayout
        else:
            klass = qt.QVBoxLayout
        self._playout = klass()
        panel.PPanelBase.__init__(self, parent, layout, style, align,
            margin, spacing, width, height)
        # Qt 4 defaults don't seem to be the same as Qt 3, so compensate
        if margin == -1:
            self.set_margin(0)
        if spacing == -1:
            self.set_spacing(0)
    
    def set_min_size(self, width, height):
        if width > -1:
            self.setMinimumWidth(width)
        if height > -1:
            self.setMinimumHeight(height)
    
    def set_box_width(self, width):
        self.setLineWidth(width)
    
    def set_margin(self, margin):
        self._playout.setContentsMargins(margin, margin, margin, margin)
    
    def set_spacing(self, spacing):
        self._playout.setSpacing(spacing)
    
    def _addwidget(self, widget):
        self._playout.addWidget(widget)
    
    def _dolayout(self):
        #self._playout.addStretch(1)
        self.setLayout(self._playout)

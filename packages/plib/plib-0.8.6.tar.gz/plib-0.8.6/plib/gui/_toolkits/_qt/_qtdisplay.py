#!/usr/bin/env python
"""
Module QTDISPLAY -- Python Qt Text Display Widgets
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for text display widgets.
"""

import qt

from plib.gui._widgets import display

from _qtcommon import _PQtWidget


class PQtTextDisplay(qt.QTextEdit, _PQtWidget, display.PTextDisplayBase):
    
    widget_class = qt.QTextEdit
    
    def __init__(self, parent, text=None, geometry=None, scrolling=False):
        qt.QTextEdit.__init__(self, parent)
        self.setReadOnly(True)
        self.setTextFormat(qt.Qt.PlainText)
        if scrolling:
            self.setWordWrap(qt.QTextEdit.NoWrap)
        display.PTextDisplayBase.__init__(self, text, geometry)
    
    def get_text(self):
        return str(self.text())
    
    def set_text(self, value):
        self.setText(value)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt text edits don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)
    
    def set_height(self, height):
        self.resize(self.width(), height)
        # Qt text edits don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumHeight(height)

#!/usr/bin/env python
"""
Module KDEDISPLAY -- Python KDE Text Display Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for text display widgets.
"""

import qt
import kdeui

from plib.gui._widgets import display

from _kdecommon import _PKDEWidget


class PKDETextDisplay(kdeui.KTextEdit, _PKDEWidget, display.PTextDisplayBase):
    
    widget_class = kdeui.KTextEdit
    
    def __init__(self, parent, text=None, geometry=None, scrolling=False):
        kdeui.KTextEdit.__init__(self, parent)
        color = self.paletteBackgroundColor()
        self.setReadOnly(True)
        # KDE forces background to disabled color on readonly
        # as well as disabled, fixup here
        self.setPaletteBackgroundColor(color)
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
        # KDE text edits don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)
    
    def set_height(self, height):
        self.resize(self.width(), height)
        # KDE text edits don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumHeight(height)

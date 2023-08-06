#!/usr/bin/env python
"""
Module KDE4DISPLAY -- Python KDE Text Display Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for text display widgets.
"""

from PyQt4 import Qt as qt
from PyKDE4 import kdeui

from plib.gui._widgets import display

from _kde4common import _PKDEWidget


class PKDETextDisplay(kdeui.KTextEdit, _PKDEWidget,
        display.PTextDisplayBase):
    
    widget_class = kdeui.KTextEdit
    
    def __init__(self, parent, text=None, geometry=None, scrolling=False):
        kdeui.KTextEdit.__init__(self, parent)
        # KDE forces background to gray on readonly as well as disabled,
        # fixup here
        palette = qt.QPalette(self.palette())
        palette.setColor(self.backgroundRole(),
            palette.color(qt.QPalette.Active, qt.QPalette.Base))
        self.setPalette(palette)
        self.setReadOnly(True)
        if scrolling:
            self.setLineWrapMode(qt.QTextEdit.NoWrap)
        display.PTextDisplayBase.__init__(self, text, geometry)
    
    def get_text(self):
        return str(self.toPlainText())
    
    def set_text(self, value):
        self.setPlainText(value)
    
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

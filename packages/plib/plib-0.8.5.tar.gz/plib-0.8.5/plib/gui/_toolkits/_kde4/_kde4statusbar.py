#!/usr/bin/env python
"""
Module KDE4STATUSBAR -- Python KDE Status Bar Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for the status bar.
"""

from PyKDE4 import kdeui

from plib.gui._base import statusbar

from _kde4common import _PKDEWidgetBase
from _kde4label import PKDETextLabel


class PKDEStatusBar(kdeui.KStatusBar, _PKDEWidgetBase,
        statusbar.PStatusBarBase):
    
    textareaclass = PKDETextLabel
    
    def __init__(self, parent, widgets=None):
        kdeui.KStatusBar.__init__(self, parent)
        statusbar.PStatusBarBase.__init__(self, parent, widgets)
        parent.setStatusBar(self)
    
    def _add_widget(self, widget, expand=False, custom=True):
        if custom:
            self.addPermanentWidget(widget, int(expand))
        else:
            self.addWidget(widget, int(expand))

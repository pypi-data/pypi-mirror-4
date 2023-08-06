#!/usr/bin/env python
"""
Module KDESTATUSBAR -- Python KDE Status Bar Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for the status bar.
"""

import kdeui

from plib.gui._base import statusbar

from _kdecommon import _PKDEWidgetBase
from _kdelabel import PKDETextLabel


class PKDEStatusBar(kdeui.KStatusBar, _PKDEWidgetBase,
    statusbar.PStatusBarBase):
    
    textareaclass = PKDETextLabel
    
    # FIXME: text is centered in status bar, and status bar doesn't show
    # tips for menu and toolbar items like it does in Qt
    
    def __init__(self, parent, widgets=None):
        kdeui.KStatusBar.__init__(self, parent)
        statusbar.PStatusBarBase.__init__(self, parent, widgets)
    
    def _add_widget(self, widget, expand=False, custom=True):
        self.addWidget(widget, int(expand), custom)

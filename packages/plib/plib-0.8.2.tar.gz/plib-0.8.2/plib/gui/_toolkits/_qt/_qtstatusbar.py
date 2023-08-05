#!/usr/bin/env python
"""
Module QTSTATUSBAR -- Python Qt Status Bar Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for the status bar.
"""

import qt

from plib.gui._base import statusbar

from _qtcommon import _PQtWidgetBase
from _qtlabel import PQtTextLabel


class PQtStatusBar(qt.QStatusBar, _PQtWidgetBase, statusbar.PStatusBarBase):
    
    textareaclass = PQtTextLabel
    
    def __init__(self, parent, widgets=None):
        qt.QStatusBar.__init__(self, parent)
        statusbar.PStatusBarBase.__init__(self, parent, widgets)
    
    def _add_widget(self, widget, expand=False, custom=True):
        self.addWidget(widget, int(expand), custom)

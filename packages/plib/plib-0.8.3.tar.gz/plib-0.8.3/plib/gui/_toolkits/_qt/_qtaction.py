#!/usr/bin/env python
"""
Module QTACTION -- Python Qt Action Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI objects for handling user actions.
"""

import qt

from plib.gui._base import action

from _qtcommon import _PQtCommunicator, _PQtWidgetBase


class PQtMenu(qt.QMenuBar, _PQtWidgetBase, action.PMenuBase):
    """Customized Qt menu class.
    """
    
    popupclass = qt.QPopupMenu
    
    def __init__(self, mainwidget):
        qt.QMenuBar.__init__(self, mainwidget, "Main Menu")
        action.PMenuBase.__init__(self, mainwidget)
    
    def _add_popup(self, title, popup):
        self.insertItem(title, popup)
    
    def _add_popup_action(self, act, popup):
        act.addTo(popup)


class PQtToolBar(qt.QToolBar, _PQtWidgetBase, action.PToolBarBase):
    """Customized Qt toolbar class.
    """
    
    def __init__(self, mainwidget):
        self._sep = False
        qt.QToolBar.__init__(self, mainwidget, "Main Toolbar")
        action.PToolBarBase.__init__(self, mainwidget)
    
    def add_action(self, act):
        act.addTo(self)
    
    def add_separator(self):
        # FIXME: doesn't appear to work on Qt 3.3.8/SuSE 11.2?
        self.addSeparator()


class PQtAction(qt.QAction, _PQtCommunicator, action.PActionBase):
    """Customized Qt action class.
    """
    
    def __init__(self, key, mainwidget):
        qt.QAction.__init__(self, mainwidget)
        self.setIconSet(qt.QIconSet(qt.QPixmap(
            self.get_icon_filename(key))))
        self.setMenuText(qt.QString(self.get_menu_str(key)))
        self.setText(qt.QString(self.get_toolbar_str(key)))
        s = self.get_accel_str(key)
        if s is not None:
            self.setAccel(qt.QKeySequence(s))
        action.PActionBase.__init__(self, key, mainwidget)
    
    def enable(self, enabled):
        self.setEnabled(enabled)

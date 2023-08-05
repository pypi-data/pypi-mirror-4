#!/usr/bin/env python
"""
Module KDEACTION -- Python KDE Action Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for handling user actions.
"""

import qt
import kdecore
import kdeui

from plib.gui._base import action

from _kdecommon import (_PKDECommunicator, _PKDEWidgetBase,
    _kdestandardicons)


class PKDEMenu(kdeui.KMenuBar, _PKDEWidgetBase, action.PMenuBase):
    """Customized KDE menu class.
    """
    
    popupclass = kdeui.KPopupMenu
    
    def __init__(self, mainwidget):
        kdeui.KMenuBar.__init__(self, mainwidget, "Main Menu")
        action.PMenuBase.__init__(self, mainwidget)
    
    def _add_popup(self, title, popup):
        self.insertItem(title, popup)
    
    def _add_popup_action(self, act, popup):
        act.addTo(popup)


class PKDEToolBar(kdeui.KToolBar, _PKDEWidgetBase, action.PToolBarBase):
    """Customized KDE toolbar class.
    """
    
    def __init__(self, mainwidget):
        self._sep = False
        kdeui.KToolBar.__init__(self, mainwidget, "Main Toolbar")
        # Icon and label stuff here instead of in the main window like in Qt
        if mainwidget.large_icons:
            self.setIconSize(self.iconSize() * 3/2, True)
        if mainwidget.show_labels:
            it = kdeui.KToolBar.IconTextBottom
        else:
            it = kdeui.KToolBar.IconOnly
        self.setIconText(it)
        action.PToolBarBase.__init__(self, mainwidget)
        # This appears to be necessary in KDE but not in Qt
        mainwidget.addDockWindow(self)
    
    def add_action(self, act):
        if self._sep:
            # Hack because the addSeparator method doesn't appear to work
            # FIXME: doesn't appear to work on KDE 3.5.10/SuSE 11.2?
            self.insertLineSeparator(act.key - 2, act.key - 2)
            self._sep = False
        act.addTo(self)
    
    def add_separator(self):
        #self.addSeparator() doesn't seem to work, hence this hack
        self._sep = True


class PKDEAction(kdeui.KAction, _PKDECommunicator, action.PActionBase):
    """Customized KDE action class.
    """
    
    def __init__(self, key, mainwidget):
        kdeui.KAction.__init__(self, mainwidget)
        # Some actions are better handled by retrieving the standard
        # icon but not using the standard action, which sets other
        # stuff differently than we want (e.g., the action text)
        if key in _kdestandardicons:
            icon = _kdestandardicons[key]
        else:
            icon = self.get_icon_filename(key)
        self.setIcon(icon)
        self.setText(qt.QString(self.get_menu_str(key)))
        self.setShortcutText(qt.QString(self.get_toolbar_str(key)))
        s = self.get_accel_str(key)
        if s is not None:
            self.setAccel(qt.QKeySequence(s))
        action.PActionBase.__init__(self, key, mainwidget)
    
    def addTo(self, widget):
        self.plug(widget, self.key)
    
    def enable(self, enabled):
        self.setEnabled(enabled)

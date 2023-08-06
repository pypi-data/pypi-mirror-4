#!/usr/bin/env python
"""
Module WXACTION -- Python wxWidgets Action Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for handling user actions.
"""

import sys

import wx

from plib.gui._base import action

from _wxcommon import _PWxCommunicator, _PWxWidgetBase, _wxstockids


def scaled_bitmap(image, factor):
    if factor is not None:
        image = image.Scale(
            image.GetWidth() * factor,
            image.GetHeight() * factor)
    return wx.BitmapFromImage(image)


class PWxPopup(wx.Menu):
    """Customized wxWidgets popup menu class.
    """
    
    def __init__(self, mainwidget):
        self.mainwidget = mainwidget
        astyle = 0
        wx.Menu.__init__(self, "", astyle)


class PWxMenu(wx.MenuBar, _PWxWidgetBase, action.PMenuBase):
    """Customized wxWidgets menu class.
    """
    
    popupclass = PWxPopup
    
    def __init__(self, mainwidget):
        astyle = 0
        wx.MenuBar.__init__(self, astyle)
        action.PMenuBase.__init__(self, mainwidget)
    
    def _add_popup(self, title, popup):
        self.Append(popup, title)
    
    def _add_popup_action(self, act, popup):
        if act._id > wx.ID_HIGHEST:
            item = wx.MenuItem(popup, act._id, act.menustr)
        else:
            item = wx.MenuItem(popup, act._id)
            #act.bitmap = item.GetBitmap()
        item.SetBitmap(scaled_bitmap(act.image, act.menufactor))
        popup.AppendItem(item)


class PWxToolBar(wx.ToolBar, _PWxWidgetBase, action.PToolBarBase):
    """Customized wxWidgets toolbar class.
    """
    
    def __init__(self, mainwidget):
        astyle = 0
        if mainwidget.show_labels:
            astyle = astyle | wx.TB_TEXT
        wx.ToolBar.__init__(self, mainwidget, style=astyle)
        action.PToolBarBase.__init__(self, mainwidget)
        self.Realize()
    
    def add_action(self, act):
        #if act._id > wx.ID_HIGHEST:
        img = scaled_bitmap(act.image, act.toolbarfactor)
        #else:
        #    img = wx.ArtProvider.GetBitmap(act._id, wx.ART_TOOLBAR)
        #    img = act.bitmap
        s = act.toolbarstr
        if self.mainwin.show_labels:
            self.AddLabelTool(act._id, s, img, shortHelp=s)
        else:
            self.AddTool(act._id, img, shortHelpString=s)
    
    def add_separator(self):
        self.AddSeparator()


class PWxAction(_PWxCommunicator, action.PActionBase):
    """Customized wxWidgets action class.
    """
    
    def __init__(self, key, mainwidget):
        self.menufactor = 0.5
        if mainwidget.large_icons:
            self.toolbarfactor = None
        else:
            self.toolbarfactor = 0.6875
        self.menustr = self.get_menu_str(key)
        self.toolbarstr = self.get_toolbar_str(key)
        self.accelstr = self.get_accel_str(key)
        if key in _wxstockids:
            self._id = _wxstockids[key]
        #    self.image = None
        else:
            self._id = wx.ID_HIGHEST + key
        self.image = wx.Image(self.get_icon_filename(key))
        action.PActionBase.__init__(self, key, mainwidget)
    
    # Need these three 'fake' widget methods to enable setup_notify mechanism
    def GetId(self):
        return self._id
    def Connect(self, *args):
        self.mainwin.Connect(*args)
    def Bind(self, event, target):
        self.mainwin.Bind(event, target, id=self._id)
    
    def enable(self, enabled):
        menu = self.mainwin.menu
        toolbar = self.mainwin.toolbar
        if menu is not None:
            menu.Enable(self._id, enabled)
        if toolbar is not None:
            toolbar.EnableTool(self._id, enabled)

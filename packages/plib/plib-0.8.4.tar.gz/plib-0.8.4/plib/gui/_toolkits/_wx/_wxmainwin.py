#!/usr/bin/env python
"""
Module WXMAINWIN -- Python wxWidgets Main Window Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI main window objects.
"""

import wx

from plib.gui.defs import *
from plib.gui._base import mainwin

from _wxcommon import _wxicons
from _wxapp import _PWxMainMixin
from _wxaction import PWxMenu, PWxToolBar, PWxAction
from _wxstatusbar import PWxStatusBar


class PWxMessageBox(mainwin.PMessageBoxBase):
    """Customized wxWidgets message box.
    """
    
    questionmap = { 
        answerYes: wx.ID_YES,
        answerNo: wx.ID_NO,
        answerCancel: wx.ID_CANCEL,
        answerOK: wx.ID_OK }
    
    def _messagebox(self, type, caption, text,
            button1, button2=None, button3=None):
        
        style = _wxicons[type]
        buttons = [button1, button2, button3]
        if (wx.ID_YES in buttons) or (wx.ID_NO in buttons):
            style = style | wx.YES_NO
        if wx.ID_OK in buttons:
            style = style | wx.OK
        if wx.ID_CANCEL in buttons:
            style = style | wx.CANCEL
        dlg = wx.MessageDialog(self._parent, text, caption, style)
        # Hack to fix strange button ordering for Yes/No/Cancel
        #b_cancel = dlg.FindWindowById(wx.ID_CANCEL)
        #b_no = dlg.FindWindowById(wx.ID_NO)
        #print b_cancel, b_no
        #if (b_cancel is not None) and (b_no is not None):
        #    b_yes = dlg.FindWindowById(wx.ID_YES)
        #    if b_yes:
        #        b_no.MoveAfterInTabOrder(b_yes)
        #    b_cancel.MoveAfterInTabOrder(b_no)
        result = dlg.ShowModal()
        dlg.Destroy()
        return result


class PWxFileDialog(mainwin.PFileDialogBase):
    
    def _wxfiledialog(self, msg, path, filter, style):
        if filter == "":
            filter = "*"
        dlg = wx.FileDialog(self._parent, msg, path, "", filter, style)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            retval = dlg.GetPath()
        else:
            retval = ""
        dlg.Destroy()
        return retval
    
    def openfiledialog(self, path, filter):
        return self._wxfiledialog("Select file to open", path, filter,
            wx.FD_OPEN)
    
    def savefiledialog(self, path, filter):
        return self._wxfiledialog("Select file to save", path, filter,
            wx.FD_SAVE)


class PWxMainWindow(_PWxMainMixin, mainwin.PMainWindowBase):
    """Customized wxWidgets main window class.
    """
    
    menuclass = PWxMenu
    toolbarclass = PWxToolBar
    statusbarclass = PWxStatusBar
    actionclass = PWxAction
    messageboxclass = PWxMessageBox
    filedialogclass = PWxFileDialog
    
    def __init__(self, parent, cls=None):
        _PWxMainMixin.__init__(self, None)
        mainwin.PMainWindowBase.__init__(self, parent, cls)
        if self.menu is not None:
            self.SetMenuBar(self.menu)
        if self.toolbar is not None:
            self.SetToolBar(self.toolbar)
        if self.statusbar is not None:
            self.SetStatusBar(self.statusbar)
        
        # 'automagic' connection
        self.setup_notify(SIGNAL_QUERYCLOSE, self.OnCloseWindow, False)
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PWxMainMixin.show_init(self)

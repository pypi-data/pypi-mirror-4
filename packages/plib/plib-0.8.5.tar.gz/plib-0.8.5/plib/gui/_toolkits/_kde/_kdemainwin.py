#!/usr/bin/env python
"""
Module KDEMAINWIN -- Python KDE Main Window Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI main window objects.
"""

import sys

import qt
import kdecore
import kdeui

from plib.gui.common import action_caption
from plib.gui.defs import *
from plib.gui._base import mainwin

from _kdecommon import _kdestandardactions, _kdemessagefuncs
from _kdeapp import _PKDEMainMixin
from _kdeaction import PKDEMenu, PKDEToolBar, PKDEAction
from _kdestatusbar import PKDEStatusBar


def _int(button):
    if button is not None:
        return button
    else:
        return 0


class PKDEMessageBox(mainwin.PMessageBoxBase):
    """Customized KDE message box.
    """
    
    questionmap = {
        answerYes: qt.QMessageBox.Yes,
        answerNo: qt.QMessageBox.No,
        answerCancel: qt.QMessageBox.Cancel,
        answerOK: qt.QMessageBox.Ok }
    
    def _messagebox(self, type, caption, text,
            button1, button2=None, button3=None):
        
        return _kdemessagefuncs[type](self._parent, caption, text,
            _int(button1), _int(button2), _int(button3))


class PKDEFileDialog(mainwin.PFileDialogBase):
    
    def openfiledialog(self, path, filter):
        return qt.QFileDialog.getOpenFileName(path, filter)
    
    def savefiledialog(self, path, filter):
        return qt.QFileDialog.getSaveFileName(path, filter)


class PKDEMainWindow(_PKDEMainMixin, mainwin.PMainWindowBase):
    """Customized KDE main window class.
    """
    
    menuclass = PKDEMenu
    toolbarclass = PKDEToolBar
    statusbarclass = PKDEStatusBar
    actionclass = PKDEAction
    messageboxclass = PKDEMessageBox
    filedialogclass = PKDEFileDialog
    
    def __init__(self, parent, cls=None):
        _PKDEMainMixin.__init__(self)
        mainwin.PMainWindowBase.__init__(self, parent, cls)
        self.setCentralWidget(self.clientwidget)
        if self.toolbar is not None:
            vmajor = qt.qVersion()[0]
            if vmajor == "2":
                self.setToolBarsMovable(False)
            elif vmajor == "3":
                self.setDockWindowsMovable(False)
            self.setDockMenuEnabled(False)
    
    def _create_action(self, key):
        if key in _kdestandardactions:
            result = _kdestandardactions[key](self, qt.SLOT("customize()"),
                self.actionCollection())
            result.__class__ = self.actionclass
            result.init_setup(key, self)
        else:
            result = mainwin.PMainWindowBase._create_action(self, key)
        # We have to do these by hand here because the KStdAction mechanism
        # doesn't seem to do them right
        if key == ACTION_PREFS:
            txt = "&Configure %s..." % self.aboutdata['name']
            result.setText(qt.QString(txt))
            result.setShortcutText(
                qt.QString(txt.replace('&', '').strip('.')))
        elif (key == ACTION_ABOUT) and ('icon' in self.aboutdata):
            result.setIcon(self.aboutdata['icon'])
        return result
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PKDEMainMixin.show_init(self)

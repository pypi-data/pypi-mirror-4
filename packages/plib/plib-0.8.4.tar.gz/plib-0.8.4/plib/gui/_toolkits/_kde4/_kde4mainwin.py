#!/usr/bin/env python
"""
Module KDE4MAINWIN -- Python KDE Main Window Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI main window objects.
"""

import sys

from PyQt4 import Qt as qt
from PyKDE4 import kdecore
from PyKDE4 import kdeui

from plib.gui.defs import *
from plib.gui._base import mainwin

from _kde4common import _kdestandardactions, _kdemessagefuncs
from _kde4app import _PKDEMainMixin
from _kde4action import PKDEMenu, PKDEToolBar, PKDEAction
from _kde4statusbar import PKDEStatusBar


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
        return qt.QFileDialog.getOpenFileName(None, "Open", path, filter)
    
    def savefiledialog(self, path, filter):
        return qt.QFileDialog.getSaveFileName(None, "Save", path, filter)


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
    
    def actionCollection(self):
        if not hasattr(self, '_actionCollection'):
            self._actionCollection = kdeui.KActionCollection(self)
        return self._actionCollection
    
    def _create_action(self, key):
        if key in _kdestandardactions:
            result = _kdestandardactions[key](self, qt.SLOT("show()"),
                self.actionCollection())
            result.__class__ = self.actionclass
            result.init_setup(key, self)
        else:
            result = mainwin.PMainWindowBase._create_action(self, key)
        # We have to do these by hand here because the KStandardAction
        # mechanism doesn't seem to do them right
        if key == ACTION_PREFS:
            txt = "&Configure %s..." % self.aboutdata['name']
            result.setText(qt.QString(txt))
            result.setToolTip(qt.QString(txt.replace('&', '').strip('.')))
        elif (key == ACTION_ABOUT) and ('icon' in self.aboutdata):
            result.setIcon(kdeui.KIcon(qt.QIcon(qt.QPixmap(
                self.aboutdata['icon']))))
        return result
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PKDEMainMixin.show_init(self)

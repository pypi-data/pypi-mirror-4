#!/usr/bin/env python
"""
Module QT4MAINWIN -- Python Qt 4 Main Window Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI main window objects.
"""

try:
    from PySide import QtGui as qt
except ImportError:
    from PyQt4 import Qt as qt

from plib.gui.defs import *
from plib.gui._base import mainwin

from _qt4common import _qtmessagefuncs
from _qt4app import _PQtMainMixin
from _qt4action import PQtMenu, PQtToolBar, PQtAction
from _qt4statusbar import PQtStatusBar


def _int(button):
    if button is not None:
        return button
    else:
        return 0


class PQtMessageBox(mainwin.PMessageBoxBase):
    """Customized Qt message box.
    """
    
    questionmap = {
        answerYes: qt.QMessageBox.Yes,
        answerNo: qt.QMessageBox.No,
        answerCancel: qt.QMessageBox.Cancel,
        answerOK: qt.QMessageBox.Ok }
    
    def _messagebox(self, type, caption, text,
            button1, button2=None, button3=None):
        
        return _qtmessagefuncs[type](self._parent, caption, text,
            _int(button1), _int(button2), _int(button3))


class PQtFileDialog(mainwin.PFileDialogBase):
    
    def openfiledialog(self, path, filter):
        return qt.QFileDialog.getOpenFileName(None, "Open",
            path, filter)
    
    def savefiledialog(self, path, filter):
        return qt.QFileDialog.getSaveFileName(None, "Save",
            path, filter)


class PQtMainWindow(_PQtMainMixin, mainwin.PMainWindowBase):
    """Customized Qt main window class.
    """
    
    menuclass = PQtMenu
    toolbarclass = PQtToolBar
    statusbarclass = PQtStatusBar
    actionclass = PQtAction
    messageboxclass = PQtMessageBox
    filedialogclass = PQtFileDialog
    
    def __init__(self, parent, cls=None):
        _PQtMainMixin.__init__(self)
        mainwin.PMainWindowBase.__init__(self, parent, cls)
        self.abouttoolkitfunc = self.app.aboutQt
        self.setCentralWidget(self.clientwidget)
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PQtMainMixin.show_init(self)

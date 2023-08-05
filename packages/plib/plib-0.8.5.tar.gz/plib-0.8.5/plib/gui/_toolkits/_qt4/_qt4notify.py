#!/usr/bin/env python
"""
Module QT4NOTIFY -- Python Qt Common Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI socket notifier objects.
"""

try:
    from PySide import QtCore as qtc
except ImportError:
    from PyQt4 import Qt as qtc

from plib.gui.defs import *

from _qt4common import _PQtCommunicator

_qtnotifytypes = {
    NOTIFY_READ: qtc.QSocketNotifier.Read,
    NOTIFY_WRITE: qtc.QSocketNotifier.Write }


class PQtSocketNotifier(_PQtCommunicator, qtc.QSocketNotifier):
    
    auto_enable = True
    
    def __init__(self, obj, notify_type, select_fn, notify_fn):
        self._obj = obj
        self.select_fn = select_fn
        self.notify_fn = notify_fn
        qtc.QSocketNotifier.__init__(self, obj.fileno(),
            _qtnotifytypes[notify_type])
        self.setup_notify(SIGNAL_NOTIFIER, self.handle_notify)
    
    def set_enabled(self, enable):
        self.setEnabled(enable)
    
    def handle_notify(self, sock):
        self.set_enabled(False)
        if (sock == self._obj.fileno()) and self.select_fn():
            self.notify_fn(self._obj)
        if self.auto_enable and self.select_fn():
            self.set_enabled(True)

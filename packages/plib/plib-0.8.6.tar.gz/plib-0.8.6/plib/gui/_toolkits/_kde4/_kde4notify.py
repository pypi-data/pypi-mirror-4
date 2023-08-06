#!/usr/bin/env python
"""
Module KDE4NOTIFY -- Python Qt Common Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI socket notifier objects.
"""

from PyQt4 import Qt as qt

from plib.gui.defs import *

from _kde4common import _PKDECommunicator

_kdenotifytypes = {
    NOTIFY_READ: qt.QSocketNotifier.Read,
    NOTIFY_WRITE: qt.QSocketNotifier.Write }


class PKDESocketNotifier(_PKDECommunicator, qt.QSocketNotifier):
    
    auto_enable = True
    
    def __init__(self, obj, notify_type, select_fn, notify_fn):
        self._obj = obj
        self.select_fn = select_fn
        self.notify_fn = notify_fn
        qt.QSocketNotifier.__init__(self, obj.fileno(),
            _kdenotifytypes[notify_type])
        self.setup_notify(SIGNAL_NOTIFIER, self.handle_notify)
    
    def set_enabled(self, enable):
        self.setEnabled(enable)
    
    def handle_notify(self, sock):
        self.set_enabled(False)
        if (sock == self._obj.fileno()) and self.select_fn():
            self.notify_fn(self._obj)
        if self.auto_enable and self.select_fn():
            self.set_enabled(True)

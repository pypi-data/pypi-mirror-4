#!/usr/bin/env python
"""
Module QTNOTIFY -- Python Qt Common Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt GUI socket notifier objects.
"""

import qt

from plib.gui.defs import *

from _qtcommon import _PQtCommunicator

_qtnotifytypes = {
    NOTIFY_READ: qt.QSocketNotifier.Read,
    NOTIFY_WRITE: qt.QSocketNotifier.Write }


class PQtSocketNotifier(_PQtCommunicator, qt.QSocketNotifier):
    
    auto_enable = True
    
    def __init__(self, obj, notify_type, select_fn, notify_fn):
        self._obj = obj
        self.select_fn = select_fn
        self.notify_fn = notify_fn
        qt.QSocketNotifier.__init__(self, obj.fileno(),
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

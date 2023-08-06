#!/usr/bin/env python
"""
Module QT4BUTTON -- Python Qt 4 Button Widgets
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI objects for button widgets.
"""

try:
    from PySide import QtGui as qt
except ImportError:
    from PyQt4 import Qt as qt

from plib.gui._widgets import button

from _qt4common import _PQtWidget


class _PQtButtonMixin(object):
    
    def set_caption(self, caption):
        self.setText(caption)


class PQtButton(qt.QPushButton, _PQtWidget, _PQtButtonMixin,
        button.PButtonBase):
    
    widget_class = qt.QPushButton
    
    def __init__(self, parent, caption=None, pxname=None,
            target=None, geometry=None):
        
        qt.QPushButton.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        button.PButtonBase.__init__(self, caption, pxname, target, geometry)
    
    def set_icon(self, pxname):
        self.setIcon(qt.QIcon(qt.QPixmap(pxname)))
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt buttons don't appear to fully respect QSizePolicy.Fixed
        self.setMinimumWidth(width)


class PQtCheckBox(qt.QCheckBox, _PQtWidget, _PQtButtonMixin,
        button.PCheckBoxBase):
    
    fn_get_checked = 'isChecked'
    fn_set_checked = 'setChecked'
    
    widget_class = qt.QCheckBox
    
    def __init__(self, parent, caption=None, pxname=None, tristate=False,
            target=None, geometry=None):
        
        qt.QCheckBox.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        button.PCheckBoxBase.__init__(self, caption, pxname, tristate,
            target, geometry)
    
    def set_icon(self, pxname):
        # FIXME: pixmaps on checkboxes?
        pass
    
    def make_tristate(self):
        self.setTriState(True)

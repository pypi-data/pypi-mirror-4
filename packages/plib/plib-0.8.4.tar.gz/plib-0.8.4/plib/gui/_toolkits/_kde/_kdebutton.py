#!/usr/bin/env python
"""
Module KDEBUTTON -- Python KDE Button Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for button widgets.
"""

import qt
import kdecore
import kdeui

from plib.gui._widgets import button

from _kdecommon import _PKDEWidget, _kdestandardicons


class _PKDEButtonMixin(object):
    
    def set_caption(self, caption):
        self.setText(caption)


class PKDEButton(kdeui.KPushButton, _PKDEWidget, _PKDEButtonMixin,
        button.PButtonBase):
    
    widget_class = kdeui.KPushButton
    
    def __init__(self, parent, caption=None, pxname=None,
            target=None, geometry=None):
        
        kdeui.KPushButton.__init__(self, parent)
        self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        # See if we're an action button with a standard icon
        if isinstance(caption, int) and (pxname == ""):
            key = caption
        elif isinstance(pxname, int):
            key = pxname
        else:
            key = None
        if key in _kdestandardicons:
            loader = kdecore.KGlobal.iconLoader()
            icon = loader.loadIcon(_kdestandardicons[key],
                kdecore.KIcon.MainToolbar)
            self.setIconSet(qt.QIconSet(icon))
            pxname = None
        # Now do standard button initialization
        button.PButtonBase.__init__(self, caption, pxname, target, geometry)
    
    def set_icon(self, pxname):
        self.setIconSet(qt.QIconSet(qt.QPixmap(pxname)))
    
    def set_width(self, width):
        self.resize(width, self.height())
        # Qt buttons don't appear to fully respect QSizePolicy.Fixed
        self.setMinimumWidth(width)


class PKDECheckBox(qt.QCheckBox, _PKDEWidget, _PKDEButtonMixin,
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

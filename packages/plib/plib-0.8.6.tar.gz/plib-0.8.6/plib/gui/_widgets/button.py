#!/usr/bin/env python
"""
Module BUTTON -- GUI Button Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for button widgets.
"""

import sys

from plib.gui.defs import *
from plib.gui._widgets import _control


class PButtonBase(_control._PDialogControl):
    """Base class for push button.
    """
    
    signal = SIGNAL_CLICKED
    
    def __init__(self, caption=None, pxname=None,
            target=None, geometry=None):
        
        if isinstance(caption, int):
            # 'caption' is actually an action key
            if pxname == "":
                pxname = caption
            caption = self.get_menu_str(caption)
        if isinstance(pxname, int):
            # 'pxname' is actually an action key
            pxname = self.get_icon_filename(pxname)
        if caption:
            self.set_caption(caption)
        if pxname:
            self.set_icon(pxname)
        _control._PDialogControl.__init__(self, target, geometry)
    
    def set_caption(self, caption):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_icon(self, pxname):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError

class PCheckBoxBase(PButtonBase):
    """ Base class for checkbox. """
    
    signal = SIGNAL_TOGGLED
    
    fn_get_checked = None
    fn_set_checked = None
    
    def __init__(self, caption=None, pxname=None,
            tristate=False, target=None, geometry=None):
        
        PButtonBase.__init__(self, caption, pxname, target, geometry)
        if tristate:
            self.make_tristate()
    
    def make_tristate(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _get_checked(self):
        return getattr(self, self.fn_get_checked)()
    
    def _set_checked(self, value):
        getattr(self, self.fn_set_checked)(value)
    
    checked = property(_get_checked, _set_checked)

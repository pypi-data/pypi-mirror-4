#!/usr/bin/env python
"""
Module DISPLAY -- GUI Text Display Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for text display widgets.
"""

from plib.gui._widgets import _control


class PTextDisplayBase(_control._PDialogControl):
    """Base class for widget that displays multiple lines of text.
    """
    
    def __init__(self, text=None, geometry=None):
        _control._PDialogControl.__init__(self, None, geometry)
        if text is not None:
            self.set_text(text)
    
    def get_text(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_text(self, value):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError

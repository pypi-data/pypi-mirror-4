#!/usr/bin/env python
"""
Module COMBO -- GUI Combo Box Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for combo box widgets.
"""

from plib.stdlib.coll import baselist, SortMixin

from plib.gui.defs import *
from plib.gui._widgets import _control


class PComboBoxBase(_control._PDialogControl, SortMixin, baselist):
    """
    Combo box that looks like a list of strings.
    
    (Note: currently selection is limited to items added to the
    combo box programmatically; the user cannot edit in the edit
    control and add new items to the pick list.)
    """
    
    signal = SIGNAL_SELECTED
    
    def __init__(self, sequence=None, target=None, geometry=None):
        _control._PDialogControl.__init__(self, target, geometry)
        baselist.__init__(self, sequence)
    
    def current_text(self):
        return self[self.current_index()]
    
    def set_current_text(self, text):
        self.set_current_index(self.index(text))
    
    def current_index(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_current_index(self, index):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError

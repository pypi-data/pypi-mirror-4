#!/usr/bin/env python
"""
Module CONTROL -- Base for GUI Dialog-Type Controls
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines an abstract base class for all dialog-type control widgets
(ones which expect to have some aspect of their geometry set by
user code).
"""

from plib.gui.common import *
from plib.gui._widgets import _signal


class _PDialogControl(_signal._PNotifyControl):
    """Base class for controls with user-defined geometry.
    
    Adds geometry-related API methods. The main use case is
    for controls within dialogs, where the layout tends to
    be specified more precisely, hence the class name.
    """
    
    def __init__(self, target=None, geometry=None):
        _signal._PNotifyControl.__init__(self, target)
        if geometry is not None:
            self.set_geometry(*geometry)
    
    def preferred_width(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def preferred_height(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_width(self, width):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_height(self, height):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_size(self, width, height):
        """Derived classes may override to implement a faster method call.
        """
        if width is not None:
            self.set_width(width)
        if height is not None:
            self.set_height(height)
    
    def set_position(self, left, top):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_geometry(self, left, top, width, height):
        """Derived classes may override to implement a faster method call.
        """
        if (width is not None) or (height is not None):
            self.set_size(width, height)
        if (left is not None) or (top is not None):
            self.set_position(left, top)

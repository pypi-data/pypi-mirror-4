#!/usr/bin/env python
"""
Module GROUPBOX -- GUI Group Box Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for group box widgets.
"""

from plib.gui._widgets import _control


class PGroupBoxBase(_control._PDialogControl):
    """Base class for group box widget.
    
    Base class for a group box with a text caption and border
    wrapping a sequence of controls given by the controls
    parameter to the constructor. 
    """
    
    def __init__(self, parent, caption, controls=None,
            margin=-1, spacing=-1, geometry=None):
        
        _control._PDialogControl.__init__(self, None, geometry)
        self._parent = parent
        self._controls = None
        self.set_caption(caption)
        if (margin > -1): self.set_margin(margin)
        if (spacing > -1): self.set_spacing(spacing)
        self._init_controls(controls)
        self._dolayout()
    
    def set_caption(self, caption):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_margin(self, margin):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_spacing(self, spacing):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _init_controls(self, controls):
        if self._controls is None:
            self._controls = []
        for control in controls:
            self._add_control(control)
            self._controls.append(control)
    
    def _add_control(self, control):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _dolayout(self):
        # Derived classes should override to do any
        # necessary creation of physical layout objects
        # after all child controls are created.
        pass

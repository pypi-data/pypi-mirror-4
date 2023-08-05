#!/usr/bin/env python
"""
Module SIGNAL -- Base for GUI Signal Emitting Controls
Sub-Package GUI.BASE of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines an abstract base class for all signal-emitting control widgets.
"""

from plib.gui.common import font_args
from plib.gui._base import _notify


class _PNotifyControl(_notify._PNotifyBase):
    """Base class for controls that send event signals.
    
    A notify control can be passed a signal target in its
    constructor. Also defines the common widget API methods.
    """
    
    fn_enable_get = None
    fn_enable_set = None
    
    def update_widget(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_colors(self, fg=None, bg=None):
        if fg is not None:
            self.set_foreground_color(fg)
        if bg is not None:
            self.set_background_color(bg)
    
    def set_foreground_color(self, color):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_background_color(self, color):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_font(self, font_name=None,
            font_size=None, bold=None, italic=None):
        
        self._set_font_object(*font_args(
            self, font_name, font_size, bold, italic))
    
    def get_font_name(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_font_size(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_font_bold(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def get_font_italic(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_font_object(self, font_name, font_size, bold, italic):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _get_enabled(self):
        return getattr(self, self.fn_enable_get)()
    
    def _set_enabled(self, value):
        getattr(self, self.fn_enable_set)(value)
    
    enabled = property(_get_enabled, _set_enabled)
    
    def set_focus(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError

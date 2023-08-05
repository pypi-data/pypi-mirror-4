#!/usr/bin/env python
"""
Module EDITCTRL -- GUI Editing Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for edit controls.
"""

from plib.gui.defs import *
from plib.gui._widgets import _control


class _PEditBase(_control._PDialogControl):
    """Base edit control class, defines standard API.
    """
    
    fn_get_text = None
    fn_set_text = None
    
    fn_get_readonly = None
    fn_set_readonly = None
    
    def _get_text(self):
        return getattr(self, self.fn_get_text)()
    
    def _set_text(self, value):
        getattr(self, self.fn_set_text)(value)
    
    edit_text = property(_get_text, _set_text)
    
    def _get_readonly(self):
        return getattr(self, self.fn_get_readonly)()
    
    def _set_readonly(self, value):
        getattr(self, self.fn_set_readonly)(value)
    
    readonly = property(_get_readonly, _set_readonly)

class PEditBoxBase(_PEditBase):
    """Base class for single-line input control.
    """
    
    signal = SIGNAL_EDITCHANGED

class PEditControlBase(_PEditBase):
    """Base class for multi-line edit control.
    """
    
    signal = SIGNAL_TEXTCHANGED
    
    def can_undo(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def can_redo(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def can_clip(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def can_paste(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def clear_edit(self):
        # Derived classes may implement a faster method
        self.edit_text = ""
    
    def undo_last(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def redo_last(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def select_all(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def delete_selected(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def copy_to_clipboard(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def cut_to_clipboard(self):
        # Derived classes may implement a faster method
        self.copy_to_clipboard()
        self.delete_selected()
    
    def paste_from_clipboard(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError

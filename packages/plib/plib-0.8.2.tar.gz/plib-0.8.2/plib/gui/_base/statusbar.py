#!/usr/bin/env python
"""
Module STATUSBAR -- GUI Status Bar Classes
Sub-Package GUI.BASE of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the status bar class.
"""


class PStatusBarBase(object):
    """Base class for status bar widget.
    
    A standard status bar with a text area on the left and an
    area for custom widgets on the right.
    
    The widgets parameter passed to the constructor should be a
    sequence of callables, each of which returns a 2-tuple: the
    first element should be an attribute name, under which the
    widget will be stored in the status bar instance, and the
    second element should be a widget suitable for insertion into
    the status bar.
    """
    
    textareaclass = None
    
    def __init__(self, mainwin, widgets=None):
        self._mainwin = mainwin
        self.create_textarea()
        self._init_widgets(widgets)
    
    def _init_widgets(self, widgets):
        if widgets is not None:
            for widget in widgets:
                self.append_widget(widget())
    
    def _add_widget(self, widget, expand=False, custom=True):
        """Placeholder for derived classes to implement
        """
        raise NotImplementedError
    
    def append_widget(self, wname, widget):
        setattr(self, wname, widget)
        self._add_widget(widget)
    
    def create_textarea(self):
        self.textarea = None
        if self.textareaclass is not None:
            self.textarea = self.textareaclass(self)
            self._add_widget(self.textarea, True, False)
    
    def get_text(self):
        return self.textarea.get_text()
    
    def set_text(self, value):
        self.textarea.set_text(value)

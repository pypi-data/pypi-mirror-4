#!/usr/bin/env python
"""
Module KDEEDITCTRL -- Python KDE Editing Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI objects for edit controls.
"""

import qt
import kdeui

from plib.gui.defs import *
from plib.gui._widgets import editctrl

from _kdecommon import _PKDEWidget, _PKDEClientWidget


class _PKDEEditMixin(object):
    
    fn_get_text = 'str_text'
    fn_set_text = 'setText'
    
    fn_get_readonly = 'isReadOnly'
    fn_set_readonly = 'set_readonly_and_color'
    
    def str_text(self):
        return str(self.text())
    
    def set_readonly_and_color(self, value):
        if value:
            color = self.paletteBackgroundColor()
        self.setReadOnly(value)
        if value:
            # KDE forces background to disabled color on readonly
            # as well as disabled, fixup here
            self.setPaletteBackgroundColor(color)


class PKDEEditBox(kdeui.KLineEdit, _PKDEWidget, _PKDEEditMixin,
        editctrl.PEditBoxBase):
    
    widget_class = kdeui.KLineEdit
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        kdeui.KLineEdit.__init__(self, parent)
        if expand:
            self._horiz = qt.QSizePolicy.MinimumExpanding
        else:
            self._horiz = qt.QSizePolicy.Fixed
        self.setSizePolicy(self._horiz, qt.QSizePolicy.Fixed)
        editctrl.PEditBoxBase.__init__(self, target, geometry)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # KDE line edits don't seem to fully respect qt.QSizePolicy.Fixed
        if self._horiz == qt.QSizePolicy.Fixed:
            self.setMaximumWidth(width)
        elif self._horiz == qt.QSizePolicy.MinimumExpanding:
            self.setMinimumWidth(width)

class PKDEEditControl(kdeui.KTextEdit, _PKDEClientWidget, _PKDEEditMixin,
        editctrl.PEditControlBase):
    
    widget_class = kdeui.KTextEdit
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        kdeui.KTextEdit.__init__(self, parent)
        self.setTextFormat(qt.Qt.PlainText)
        if scrolling:
            self.setWordWrap(qt.QTextEdit.NoWrap)
        editctrl.PEditControlBase.__init__(self, target, geometry)
        # Signal connections for tracking state
        for signame in ['undo', 'redo', 'copy']:
            qt.QObject.connect(self, qt.SIGNAL("%sAvailable(bool)" % signame),
                self._state_changed)
    
    def set_width(self, width):
        self.resize(width, self.height())
        # KDE text edits don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumWidth(width)
    
    def set_height(self, height):
        self.resize(self.width(), height)
        # KDE text edits don't seem to fully respect
        # qt.QSizePolicy.MinimumExpanding
        self.setMinimumHeight(height)
    
    def textStateChanged(self):
        self.do_notify(SIGNAL_TEXTSTATECHANGED)
    
    def _state_changed(self, available):
        self.textStateChanged()
    
    def can_undo(self):
        return self.isUndoRedoEnabled() and self.isUndoAvailable()
    
    def can_redo(self):
        return self.isUndoRedoEnabled() and self.isRedoAvailable()
    
    def can_clip(self):
        return self.hasSelectedText()
    
    def can_paste(self):
        return True # FIXME: self.canPaste()?
    
    def clear_edit(self):
        self.clear()
    
    def undo_last(self):
        self.undo()
    
    def redo_last(self):
        self.redo()
    
    def select_all(self):
        self.selectAll()
    
    def delete_selected(self):
        self.removeSelectedText()
    
    def copy_to_clipboard(self):
        self.copy()
    
    def cut_to_clipboard(self):
        self.cut()
    
    def paste_from_clipboard(self):
        self.paste()
        # KDE 3 doesn't appear to fire this automatically on a paste
        self.textStateChanged()

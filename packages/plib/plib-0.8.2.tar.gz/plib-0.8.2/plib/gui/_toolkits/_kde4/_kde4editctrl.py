#!/usr/bin/env python
"""
Module KDE4EDITCTRL -- Python KDE Editing Widgets
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE 4 GUI objects for edit controls.
"""

from PyQt4 import Qt as qt
from PyKDE4 import kdeui

from plib.gui.defs import *
from plib.gui._widgets import editctrl

from _kde4common import _PKDEWidget, _PKDEClientWidget


class _PKDEEditMixin(object):
    
    fn_get_readonly = 'isReadOnly'
    fn_set_readonly = 'set_readonly_and_color'
    
    def set_readonly_and_color(self, value):
        if value and not self.isReadOnly():
            # KDE forces background to gray on readonly as well as disabled,
            # fixup here
            palette = qt.QPalette(self.palette())
            palette.setColor(self.backgroundRole(),
                palette.color(qt.QPalette.Active, qt.QPalette.Base))
            self.setPalette(palette)
        self.setReadOnly(value)


class PKDEEditBox(kdeui.KLineEdit, _PKDEWidget, _PKDEEditMixin,
        editctrl.PEditBoxBase):
    
    fn_get_text = 'str_text'
    fn_set_text = 'setText'
    
    widget_class = kdeui.KLineEdit
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        kdeui.KLineEdit.__init__(self, parent)
        if expand:
            self._horiz = qt.QSizePolicy.MinimumExpanding
        else:
            self._horiz = qt.QSizePolicy.Fixed
        self.setSizePolicy(self._horiz, qt.QSizePolicy.Fixed)
        editctrl.PEditBoxBase.__init__(self, target, geometry)
    
    def str_text(self):
        return str(self.text())
    
    def set_width(self, width):
        self.resize(width, self.height())
        # KDE line edits don't seem to fully respect qt.QSizePolicy.Fixed
        if self._horiz == qt.QSizePolicy.Fixed:
            self.setMaximumWidth(width)
        elif self._horiz == qt.QSizePolicy.MinimumExpanding:
            self.setMinimumWidth(width)


class PKDEEditControl(kdeui.KTextEdit, _PKDEClientWidget, _PKDEEditMixin,
        editctrl.PEditControlBase):
    
    fn_get_text = 'str_plaintext'
    fn_set_text = 'setPlainText'
    
    widget_class = kdeui.KTextEdit
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        # Flags for tracking state
        self._undoflag = False
        self._redoflag = False
        self._clipflag = False
        
        kdeui.KTextEdit.__init__(self, parent)
        self.setAcceptRichText(False)
        if scrolling:
            self.setLineWrapMode(qt.QTextEdit.NoWrap)
        editctrl.PEditControlBase.__init__(self, target, geometry)
        
        # Signal connections for tracking state
        statesigs = [
            ("undo", self._check_undoflag),
            ("redo", self._check_redoflag),
            ("copy", self._check_clipflag) ]
        for signame, target in statesigs:
            qt.QObject.connect(self, qt.SIGNAL("%sAvailable(bool)" % signame),
                target)
    
    def str_plaintext(self):
        return str(self.toPlainText())
    
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
    
    def _check_undoflag(self, available):
        self._undoflag = available
        self.textStateChanged()
    
    def _check_redoflag(self, available):
        self._redoflag = available
        self.textStateChanged()
    
    def _check_clipflag(self, available):
        self._clipflag = available
        self.textStateChanged()
    
    def can_undo(self):
        return self.isUndoRedoEnabled() and self._undoflag
    
    def can_redo(self):
        return self.isUndoRedoEnabled() and self._redoflag
    
    def can_clip(self):
        return self._clipflag
    
    def can_paste(self):
        return self.canPaste()
    
    def clear_edit(self):
        self.clear()
    
    def undo_last(self):
        self.undo()
    
    def redo_last(self):
        self.redo()
    
    def select_all(self):
        self.selectAll()
    
    def delete_selected(self):
        pass # FIXME
    
    def copy_to_clipboard(self):
        self.copy()
    
    def cut_to_clipboard(self):
        self.cut()
    
    def paste_from_clipboard(self):
        self.paste()

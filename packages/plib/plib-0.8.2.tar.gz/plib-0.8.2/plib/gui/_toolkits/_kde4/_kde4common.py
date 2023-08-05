#!/usr/bin/env python
"""
Module KDE4COMMON -- Python KDE Common Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common KDE 4 GUI objects for use by the other
KDE 4 modules.
"""

from abc import ABCMeta

from PyQt4 import Qt as qt
from PyKDE4 import kdeui

from plib.gui.defs import *

_kdestandardnames = {
    ACTION_FILENEW: 'openNew',
    ACTION_FILEOPEN: 'open',
    ACTION_FILESAVE: 'save',
    ACTION_FILESAVEAS: 'saveAs',
    ACTION_FILECLOSE: 'close',
    ACTION_EDITUNDO: 'undo',
    ACTION_EDITREDO: 'redo',
    ACTION_EDITCUT: 'cut',
    ACTION_EDITCOPY: 'copy',
    ACTION_EDITPASTE: 'paste',
    ACTION_PREFS: 'preferences',
    ACTION_ABOUT: 'aboutApp',
    ACTION_ABOUTTOOLKIT: 'aboutKDE',
}

_kdestandardactions = dict((key, getattr(kdeui.KStandardAction, name))
    for key, name in _kdestandardnames.iteritems())

# There is duplication between here and _kdestandardnames because
# action buttons can't use KStandardAction, but they can use the
# standard icons if present

_kdestandardicons = {
    ACTION_FILENEW: "document-new",
    ACTION_FILEOPEN: "document-open",
    ACTION_FILESAVE: "document-save",
    ACTION_FILESAVEAS: "document-save-as",
    ACTION_FILECLOSE: "window-close",
    ACTION_EDITUNDO: "edit-undo",
    ACTION_EDITREDO: "edit-redo",
    ACTION_EDITCUT: "edit-cut",
    ACTION_EDITCOPY: "edit-copy",
    ACTION_EDITPASTE: "edit-paste",
    ACTION_EDITDELETE: "edit-delete",
    ACTION_EDITSELECTALL: "edit-select-all",
    ACTION_VIEW: "view-fullscreen",
    #ACTION_EDIT
    ACTION_REFRESH: "view-refresh",
    ACTION_ADD: "list-add",
    ACTION_REMOVE: "list-remove",
    #ACTION_APPLY
    ACTION_COMMIT: "document-send",
    ACTION_ROLLBACK: "document-revert",
    #ACTION_OK
    #ACTION_CANCEL
    #ACTION_ABOUT
    #ACTION_ABOUTTOOLKIT
    ACTION_EXIT: "application-exit"
}

_kdealignmap = {
    ALIGN_LEFT: qt.Qt.AlignLeft | qt.Qt.AlignVCenter,
    ALIGN_CENTER: qt.Qt.AlignCenter,
    ALIGN_RIGHT: qt.Qt.AlignRight | qt.Qt.AlignVCenter }

_kdecolormap = dict((color, qt.QColor(color.lower()))
    for color in COLORNAMES)

_kdemessagefuncs = {
    MBOX_INFO: qt.QMessageBox.information,
    MBOX_WARN: qt.QMessageBox.warning,
    MBOX_ERROR: qt.QMessageBox.critical,
    MBOX_QUERY: qt.QMessageBox.question }

_kdesignalmap = {
    SIGNAL_ACTIVATED: "triggered()",
    SIGNAL_CLICKED: "clicked()",
    SIGNAL_TOGGLED: "clicked()", # toggled(bool)?
    SIGNAL_SELECTED: "activated(int)",
    SIGNAL_LISTSELECTED: "currentItemChanged(QTreeWidgetItem*, QTreeWidgetItem*)",
    SIGNAL_CELLSELECTED: "currentCellChanged(int, int, int, int)",
    SIGNAL_TABLECHANGED: "cellChanged(int, int)",
    SIGNAL_TEXTCHANGED: "textChanged()", # textEdited()?
    SIGNAL_EDITCHANGED: "textChanged(const QString&)", # textEdited(const QString&)?
    SIGNAL_ENTER: "returnPressed()",
    SIGNAL_TABCHANGED: "currentChanged(int)",
    SIGNAL_NOTIFIER: "activated(int)",
    SIGNAL_BEFOREQUIT: "aboutToQuit()" }

_kdeeventmap = {
    SIGNAL_TEXTSTATECHANGED: "textStateChanged",
    SIGNAL_FOCUS_IN: "focusInEvent",
    SIGNAL_FOCUS_OUT: "focusOutEvent",
    SIGNAL_CLOSING: "closeEvent",
    SIGNAL_HIDDEN: "hideEvent" }


def _kdemap(signal):
    if signal in _kdesignalmap:
        return qt.SIGNAL(_kdesignalmap[signal])
    elif signal in _kdeeventmap:
        return qt.SIGNAL(_kdeeventmap[signal])
    else:
        return None


# Ugly hack to fix metaclass conflict for classes that use the collection
# ABCs

_KDEMeta = type(qt.QObject)


class _PKDEMeta(ABCMeta, _KDEMeta):
    
    def __init__(cls, name, bases, attrs):
        _KDEMeta.__init__(cls, name, bases, attrs)
        ABCMeta.__init__(cls, name, bases, attrs)


# NOTE: we don't need to define 'wrapper' methods here as we do under GTK and
# wxWidgets because Qt silently discards any extra parameters that are not
# accepted by a signal handler. (BTW, this is good because wrappers don't seem
# to work like they should in Qt -- see PEDIT.PY, PEditor._setup_signals.)

class _PKDECommunicator(object):
    """Mixin class to abstract signal/slot functionality in KDE.
    """
    
    def setup_notify(self, signal, target):
        if signal in _kdeeventmap:
            # hack to make KDE event methods look like signals
            if not hasattr(self, _kdeeventmap[signal]):
                return
            self.enabled_events[signal] = True
        qt.QObject.connect(self, _kdemap(signal), target)
    
    def do_notify(self, signal, *args):
        sig = _kdemap(signal)
        if sig is not None:
            self.emit(sig, args)
    
    # need the following for widget events that have to have an overridden
    # handler defined in the class (can't "substitute on the fly") so that
    # they can work like signals
    
    enabled_events = {}
    
    def _emit_event(self, signal):
        if signal in self.enabled_events:
            self.do_notify(signal)


class _PKDEWidgetBase(object):
    """Mixin class to provide minimal KDE widget methods.
    """
    
    fn_enable_get = 'isEnabled'
    fn_enable_set = 'setEnabled'
    
    def update_widget(self):
        self.update()
    
    def preferred_width(self):
        return max(self.minimumSize().width(), self.sizeHint().width())
    
    def preferred_height(self):
        return max(self.minimumSize().height(), self.sizeHint().height())
    
    def set_width(self, width):
        self.resize(width, self.height())
    
    def set_height(self, height):
        self.resize(self.width(), height)
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self.move(left, top)
    
    def _mapped_color(self, color):
        if isinstance(color, qt.QColor):
            return color
        return _kdecolormap[color]
    
    def set_colors(self, fg=None, bg=None):
        palette = qt.QPalette(self.palette())
        if fg is not None:
            palette.setColor(self.foregroundRole(), self._mapped_color(fg))
        if bg is not None:
            self.setAutoFillBackground(True)
            palette.setColor(self.backgroundRole(), self._mapped_color(bg))
        self.setPalette(palette)
    
    def set_foreground_color(self, color):
        self.set_colors(fg=color)
    
    def set_background_color(self, color):
        self.set_colors(bg=color)
    
    def get_font_name(self):
        return self.font().family()
    
    def get_font_size(self):
        return self.font().pointSize()
    
    def get_font_bold(self):
        return self.font().bold()
    
    def get_font_italic(self):
        return self.font().italic()
    
    def _qt_font_object(self, font_name, font_size, bold, italic):
        font = qt.QFont(font_name, font_size)
        font.setBold(bold)
        font.setItalic(italic)
        return font
    
    def _set_font_object(self, font_name, font_size, bold, italic):
        self.setFont(self._qt_font_object(font_name, font_size, bold, italic))
    
    def set_focus(self):
        self.setFocus()


class _PKDEWidget(_PKDECommunicator, _PKDEWidgetBase):
    """Mixin class for KDE widgets that can send/receive signals.
    """
    
    widget_class = None
    
    def focusInEvent(self, event):
        self.widget_class.focusInEvent(self, event)
        self._emit_event(SIGNAL_FOCUS_IN)
    
    def focusOutEvent(self, event):
        self.widget_class.focusOutEvent(self, event)
        self._emit_event(SIGNAL_FOCUS_OUT)


class _PKDEClientWidget(_PKDEWidget):
    """Mixin class for KDE main window client widgets.
    """
    pass

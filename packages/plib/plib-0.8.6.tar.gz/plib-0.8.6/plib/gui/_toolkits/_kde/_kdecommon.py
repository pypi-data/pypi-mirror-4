#!/usr/bin/env python
"""
Module KDECOMMON -- Python KDE Common Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common KDE GUI objects for use by the other
KDE modules.
"""

from abc import ABCMeta

import qt
import kdeui

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
    #ACTION_ABOUTTOOLKIT: 'aboutKDE',  # FIXME: doesn't always work in KDE 3?
}

_kdestandardactions = dict((key, getattr(kdeui.KStdAction, name))
    for key, name in _kdestandardnames.iteritems())

# There is duplication between here and _kdestandardnames because
# action buttons can't use KStdAction, but they can use the
# standard icons if present

_kdestandardicons = {
    ACTION_FILENEW: "filenew",
    ACTION_FILEOPEN: "fileopen",
    ACTION_FILESAVE: "filesave",
    ACTION_FILESAVEAS: "filesaveas",
    ACTION_FILECLOSE: "fileclose",
    ACTION_EDITUNDO: "undo",
    ACTION_EDITREDO: "redo",
    ACTION_EDITCUT: "editcut",
    ACTION_EDITCOPY: "editcopy",
    ACTION_EDITPASTE: "editpaste",
    ACTION_EDITDELETE: "editdelete",
    #ACTION_EDITSELECTALL
    ACTION_VIEW: "window_fullscreen",
    ACTION_EDIT: "edit",
    ACTION_REFRESH: "reload",
    ACTION_ADD: "add",
    ACTION_REMOVE: "remove",
    ACTION_APPLY: "apply",
    ACTION_COMMIT: "next",
    ACTION_ROLLBACK: "stop",
    ACTION_OK: "button_ok",
    ACTION_CANCEL: "button_cancel",
    #ACTION_PREFS
    ACTION_ABOUT: "messagebox_info",
    ACTION_ABOUTTOOLKIT: "about_kde",
    ACTION_EXIT: "exit"
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
    SIGNAL_ACTIVATED: "activated()",
    SIGNAL_CLICKED: "clicked()",
    SIGNAL_TOGGLED: "clicked()",
    SIGNAL_SELECTED: "activated(int)",
    SIGNAL_LISTSELECTED: "currentChanged(QListViewItem*)",
    SIGNAL_CELLSELECTED: "currentChanged(int, int)",
    SIGNAL_TABLECHANGED: "valueChanged(int, int)",
    SIGNAL_TEXTCHANGED: "textChanged()",
    SIGNAL_EDITCHANGED: "textChanged(const QString&)",
    SIGNAL_ENTER: "returnPressed(const QString&)",
    SIGNAL_TABCHANGED: "currentChanged(QWidget*)",
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
        return qt.PYSIGNAL(_kdeeventmap[signal])
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
    
    def set_foreground_color(self, color):
        self.setPaletteForegroundColor(self._mapped_color(color))
    
    def set_background_color(self, color):
        self.setPaletteBackgroundColor(self._mapped_color(color))
    
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
        self.setFont(self._qt_font_object(
            font_name, font_size, bold, italic))
    
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

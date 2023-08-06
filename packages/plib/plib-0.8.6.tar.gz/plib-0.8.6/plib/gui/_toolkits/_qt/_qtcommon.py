#!/usr/bin/env python
"""
Module QTCOMMON -- Python Qt Common Objects
Sub-Package GUI.TOOLKITS.QT of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common Qt GUI objects for use by the other
Qt modules.
"""

from abc import ABCMeta

import qt

from plib.gui.defs import *

_qtalignmap = {
    ALIGN_LEFT: qt.Qt.AlignLeft | qt.Qt.AlignVCenter,
    ALIGN_CENTER: qt.Qt.AlignCenter,
    ALIGN_RIGHT: qt.Qt.AlignRight | qt.Qt.AlignVCenter }

_qtcolormap = dict((color, qt.QColor(color.lower()))
    for color in COLORNAMES)

_qtmessagefuncs = {
    MBOX_INFO: qt.QMessageBox.information,
    MBOX_WARN: qt.QMessageBox.warning,
    MBOX_ERROR: qt.QMessageBox.critical,
    MBOX_QUERY: qt.QMessageBox.question }

_qtsignalmap = {
    SIGNAL_ACTIVATED: "activated()",
    SIGNAL_CLICKED: "clicked()",
    SIGNAL_TOGGLED: "clicked()",
    SIGNAL_SELECTED: "activated(int)",
    SIGNAL_LISTSELECTED: "currentChanged(QListViewItem*)",
    SIGNAL_CELLSELECTED: "currentChanged(int, int)",
    SIGNAL_TABLECHANGED: "valueChanged(int, int)",
    SIGNAL_TEXTCHANGED: "textChanged()",
    SIGNAL_EDITCHANGED: "textChanged(const QString&)",
    SIGNAL_ENTER: "returnPressed()",
    SIGNAL_TABCHANGED: "currentChanged(QWidget*)",
    SIGNAL_NOTIFIER: "activated(int)",
    SIGNAL_BEFOREQUIT: "aboutToQuit()" }

_qteventmap = {
    SIGNAL_TEXTSTATECHANGED: "textStateChanged",
    SIGNAL_FOCUS_IN: "focusInEvent",
    SIGNAL_FOCUS_OUT: "focusOutEvent",
    SIGNAL_CLOSING: "closeEvent",
    SIGNAL_HIDDEN: "hideEvent" }


def _qtmap(signal):
    if signal in _qtsignalmap:
        return qt.SIGNAL(_qtsignalmap[signal])
    elif signal in _qteventmap:
        return qt.PYSIGNAL(_qteventmap[signal])
    else:
        return None


# Ugly hack to fix metaclass conflict for classes that use the collection
# ABCs

_QtMeta = type(qt.QObject)


class _PQtMeta(ABCMeta, _QtMeta):
    
    def __init__(cls, name, bases, attrs):
        _QtMeta.__init__(cls, name, bases, attrs)
        ABCMeta.__init__(cls, name, bases, attrs)


# NOTE: we don't need to define 'wrapper' methods here as we do under GTK and
# wxWidgets because Qt silently discards any extra parameters that are not
# accepted by a signal handler. (BTW, this is good because wrappers don't seem
# to work like they should in Qt -- see _edit.py ``PEditor._setup_signals``.)

class _PQtCommunicator(object):
    """Mixin class to abstract signal/slot functionality in Qt.
    """
    
    def setup_notify(self, signal, target):
        if signal in _qteventmap:
            # hack to make Qt event methods look like signals
            if not hasattr(self, _qteventmap[signal]):
                return
            self.enabled_events[signal] = True
        qt.QObject.connect(self, _qtmap(signal), target)
    
    def do_notify(self, signal, *args):
        sig = _qtmap(signal)
        if sig is not None:
            self.emit(sig, args)
    
    # need the following for widget events that have to have an overridden
    # handler defined in the class (can't "substitute on the fly") so that
    # they can work like signals
    
    enabled_events = {}
    
    def _emit_event(self, signal):
        if signal in self.enabled_events:
            self.do_notify(signal)


class _PQtWidgetBase(object):
    """Mixin class to provide minimal Qt widget methods.
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
        return _qtcolormap[color]
    
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


class _PQtWidget(_PQtCommunicator, _PQtWidgetBase):
    """Mixin class for Qt widgets that can send/receive signals.
    """
    
    widget_class = None
    
    def focusInEvent(self, event):
        self.widget_class.focusInEvent(self, event)
        self._emit_event(SIGNAL_FOCUS_IN)
    
    def focusOutEvent(self, event):
        self.widget_class.focusOutEvent(self, event)
        self._emit_event(SIGNAL_FOCUS_OUT)


class _PQtClientWidget(_PQtWidget):
    """Mixin class for Qt main window client widgets.
    """
    pass

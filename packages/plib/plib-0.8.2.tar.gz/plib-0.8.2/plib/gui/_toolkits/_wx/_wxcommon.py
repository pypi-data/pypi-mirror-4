#!/usr/bin/env python
"""
Module WXCOMMON -- Python wxWidgets Common Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI common objects.
"""

import string

import wx
import wx.grid
from wx.lib.evtmgr import eventManager
from wx.lib.newevent import NewEvent

from plib.gui.defs import *

# Style constant for edit controls that are scrolling

_wx_ec_scroll_style = wx.VSCROLL | wx.HSCROLL | wx.TE_DONTWRAP

# FIXME: These are only good for buttons and menus, and the toolbar ones
# in wx.ArtProvider don't match all the ids! WTF!@#$%^&*()
_wxstockids = {
    ACTION_FILENEW: wx.ID_NEW,
    ACTION_FILEOPEN: wx.ID_OPEN,
    ACTION_FILESAVE: wx.ID_SAVE,
    ACTION_FILESAVEAS: wx.ID_SAVEAS,
    ACTION_FILECLOSE: wx.ID_CLOSE,
    ACTION_EDIT: wx.ID_EDIT,
    ACTION_EDITUNDO: wx.ID_UNDO,
    ACTION_EDITREDO: wx.ID_REDO,
    ACTION_EDITCUT: wx.ID_CUT,
    ACTION_EDITCOPY: wx.ID_COPY,
    ACTION_EDITPASTE: wx.ID_PASTE,
    ACTION_EDITDELETE: wx.ID_DELETE,
    ACTION_EDITSELECTALL: wx.ID_SELECTALL,
    ACTION_REFRESH: wx.ID_REFRESH,
    ACTION_ADD: wx.ID_ADD,
    ACTION_REMOVE: wx.ID_REMOVE,
    ACTION_APPLY: wx.ID_APPLY,
    ACTION_OK: wx.ID_OK,
    ACTION_CANCEL: wx.ID_CANCEL,
    ACTION_PREFS: wx.ID_PREFERENCES,
    ACTION_ABOUT: wx.ID_ABOUT,
    ACTION_EXIT: wx.ID_EXIT }

_wxalignmap = {
    ALIGN_LEFT: wx.LIST_FORMAT_LEFT,
    ALIGN_CENTER: wx.LIST_FORMAT_CENTRE,
    ALIGN_RIGHT: wx.LIST_FORMAT_RIGHT }

_wxicons = {
    MBOX_INFO: wx.ICON_INFORMATION,
    MBOX_WARN: wx.ICON_EXCLAMATION,
    MBOX_ERROR: wx.ICON_ERROR,
    MBOX_QUERY: wx.ICON_QUESTION }

_wxfontfamilies = {
    wx.FONTFAMILY_ROMAN: ["Times New Roman"],
    wx.FONTFAMILY_SWISS: ["Arial", "Verdana"],
    wx.FONTFAMILY_MODERN: ["Courier New"] }

# Define our own custom events
ClosingEvent, EVT_CLOSING = NewEvent()
TextStateEvent, EVT_TEXT_STATE_CHANGED = NewEvent()

_wxcustommap = {
    SIGNAL_TEXTSTATECHANGED: TextStateEvent,
    SIGNAL_CLOSING: ClosingEvent }

_wxeventmap = {
    SIGNAL_ACTIVATED: wx.EVT_MENU,
    SIGNAL_CLICKED: wx.EVT_BUTTON,
    SIGNAL_TOGGLED: wx.EVT_CHECKBOX,
    SIGNAL_SELECTED: wx.EVT_COMBOBOX,
    SIGNAL_FOCUS_IN: wx.EVT_SET_FOCUS,
    SIGNAL_FOCUS_OUT: wx.EVT_KILL_FOCUS,
    SIGNAL_LISTSELECTED: wx.EVT_TREE_SEL_CHANGED,
    SIGNAL_CELLSELECTED: wx.grid.EVT_GRID_SELECT_CELL,
    SIGNAL_TABLECHANGED: wx.grid.EVT_GRID_CELL_CHANGE,
    SIGNAL_TEXTCHANGED: wx.EVT_TEXT,
    SIGNAL_TEXTSTATECHANGED: EVT_TEXT_STATE_CHANGED,
    SIGNAL_EDITCHANGED: wx.EVT_TEXT,
    SIGNAL_ENTER: wx.EVT_TEXT_ENTER,
    SIGNAL_TABCHANGED: wx.EVT_NOTEBOOK_PAGE_CHANGED,
    SIGNAL_CLOSING: EVT_CLOSING,
    SIGNAL_HIDDEN: wx.EVT_WINDOW_DESTROY,
    SIGNAL_QUERYCLOSE: wx.EVT_CLOSE,
    SIGNAL_BEFOREQUIT: wx.EVT_WINDOW_DESTROY }


# 'Wrapper' functions for certain events to repackage parameters

def wx_plain_wrapper(self, target):
    def wrapper(event):
        target()
    return wrapper


def wx_selected_wrapper(self, target):
    def wrapper(event):
        target(self.GetSelection())
    return wrapper


def wx_listviewchanged_wrapper(self, target):
    def wrapper(event):
        item = self.GetItemPyData(event.GetItem())
        # Hack to filter out events fired too soon by some Wx versions
        if item is not None:
            target(item)
    return wrapper


def wx_cellselected_wrapper(self, target):
    def wrapper(event):
        # FIXME: As noted in scrips-edit.py, we have to have hacks
        # in user code to work around the fact that wx fires this
        # event and the table changed event out of sequence; when
        # you press Enter to finish a cell edit, wx in its infinite
        # wisdom moves the cell cursor to the next cell down, but it
        # does *NOT* fire the table changed event *before* moving the
        # cursor; no, it first moves the cursor *AND FIRES THE CELL
        # SELECTED EVENT*, and THEN it *FIRES THE TABLE CHANGED EVENT
        # FOR THE CELL THAT IS NO LONGER SELECTED BECAUSE IT MOVED
        # THE CURSOR BEFORE TELLING USER CODE THAT THE PREVIOUS CELL
        # HAD BEEN CHANGED* @#$%^&*! Anyway, at some point I may
        # figure out a way to have the library code here fix this
        # f**ked event ordering, so user code sees an API that makes
        # some kind of f**king sense.
        target(event.GetRow(), event.GetCol())
        event.Skip(True)
    return wrapper


def wx_tablechanged_wrapper(self, target):
    def wrapper(event):
        print event, event.GetRow(), event.GetCol()
        target(event.GetRow(), event.GetCol())
    return wrapper


def wx_tabchanged_wrapper(self, target):
    def wrapper(event):
        target(self._items[event.GetSelection()])
    return wrapper


_wxwrappermap = {
    SIGNAL_ACTIVATED: wx_plain_wrapper,
    SIGNAL_CLICKED: wx_plain_wrapper,
    SIGNAL_TOGGLED: wx_plain_wrapper,
    SIGNAL_SELECTED: wx_selected_wrapper,
    SIGNAL_FOCUS_IN: wx_plain_wrapper,
    SIGNAL_FOCUS_OUT: wx_plain_wrapper,
    SIGNAL_LISTSELECTED: wx_listviewchanged_wrapper,
    SIGNAL_CELLSELECTED: wx_cellselected_wrapper,
    SIGNAL_TABLECHANGED: wx_tablechanged_wrapper,
    SIGNAL_TEXTCHANGED: wx_plain_wrapper,
    SIGNAL_EDITCHANGED: wx_plain_wrapper,
    SIGNAL_ENTER: wx_plain_wrapper,
    SIGNAL_TABCHANGED: wx_tabchanged_wrapper,
    SIGNAL_CLOSING: wx_plain_wrapper,
    SIGNAL_HIDDEN: wx_plain_wrapper }


class _PWxCommunicator(object):
    """Mixin class to abstract notification functionality in wxWidgets.
    """
    
    def setup_notify(self, signal, target, wrap=True):
        if signal in _wxeventmap:
            event = _wxeventmap[signal]
            if wrap and (signal in _wxwrappermap):
                handler = _wxwrappermap[signal](self, target)
            else:
                handler = target
            
            # Do the following instead of self.Bind(event, handler) so
            # that multiple handlers can receive a single event
            eventManager.Register(handler, event, self)
    
    def do_notify(self, signal, *args):
        if signal in _wxcustommap:
            event = _wxcustommap[signal]()
        elif signal in _wxeventmap:
            event = wx.Event()
            event.SetEventType(_wxeventmap[signal])
            if hasattr(self, 'id'):
                event.SetEventID(self.id)
            elif hasattr(self, '_id'):
                event.SetEventID(self._id)
            elif hasattr(self, 'GetId'):
                event.SetEventID(self.GetId())
        if event is not None:
            event.SetEventObject(self)
            self.AddPendingEvent(event)


_wx_font_weights = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_BOLD]
_wx_font_styles = [wx.FONTSTYLE_NORMAL, wx.FONTSTYLE_ITALIC]


class _PWxWidgetBase(object):
    """Mixin class to provide basic wx widget methods.
    """
    
    fn_enable_get = 'IsEnabled'
    fn_enable_set = 'Enable'
    
    _depth_test_str = string.ascii_letters + string.digits
    _depth_scale_factor = 1.3
    
    def update_widget(self):
        self.Refresh()
    
    def preferred_width(self):
        return self.GetSizeTuple()[0]
    
    def preferred_height(self):
        return self.GetSizeTuple()[1]
    
    def set_width(self, width):
        height = self.GetSizeTuple()[1]
        self.SetSizeWH(width, height)
        self.SetMinSize((width, height))
    
    def set_height(self, height):
        width = self.GetSizeTuple()[0]
        self.SetSizeWH(width, height)
        self.SetMinSize((width, height))
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self.SetPosition(wx.Point(left, top))
    
    def set_foreground_color(self, color):
        self.SetForegroundColour(color)
    
    def set_background_color(self, color):
        self.SetBackgroundColour(color)
    
    def get_font_name(self):
        return self.GetFont().GetFaceName()
    
    def get_font_size(self):
        return self.GetFont().GetPointSize()
    
    def get_font_bold(self):
        return (self.GetFont().GetWeight() == _wx_font_weights[1])
    
    def get_font_italic(self):
        return (self.GetFont().GetStyle() == _wx_font_styles[1])
    
    def _wx_font_object(self, font_name, font_size, bold, italic):
        font_family = wx.FONTFAMILY_DEFAULT
        for family, names in _wxfontfamilies.iteritems():
            if font_name in names:
                font_family = family
                break
        font_style = _wx_font_styles[int(italic)]
        font_weight = _wx_font_weights[int(bold)]
        font = wx.Font(font_size, font_family, font_style, font_weight)
        font.SetFaceName(font_name)
        return font
    
    def _set_font_object(self, font_name, font_size, bold, italic):
        font = self._wx_font_object(font_name, font_size, bold, italic)
        if hasattr(self, '_depth_w'):
            # Hack to make list view column auto-sizing work correctly
            # on font change
            old_extent = self.GetTextExtent(self._depth_test_str)[0]
            new_extent = self.GetFullTextExtent(self._depth_test_str, font)[0]
            self._depth_w = int(
                self._depth_w * self._depth_scale_factor * new_extent /
                old_extent)
        self.SetFont(font)
        if hasattr(self, 'SetDefaultCellFont'):
            self.SetDefaultCellFont(font) # takes care of the table widget
        if hasattr(self, 'AutoSizeCols'):
            self.AutoSizeCols() # this takes care of the list view widget
    
    def set_focus(self):
        self.SetFocus()


class _PWxWidget(_PWxCommunicator, _PWxWidgetBase):
    """Mixin class for wx widgets that can send/receive signals.
    """
    pass


class _PWxClientWidget(_PWxWidget):
    """Mixin class for wx main window client widgets.
    """
    pass

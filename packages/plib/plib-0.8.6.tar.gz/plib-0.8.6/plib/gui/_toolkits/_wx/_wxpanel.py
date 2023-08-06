#!/usr/bin/env python
"""
Module WXPANEL -- Python wxWidgets Panel Objects
Sub-Package GUI.TOOLKITS.WX of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the wxWidgets GUI objects for the panel widgets.
"""

import wx

from plib.gui.defs import *

from plib.gui._widgets import panel

from _wxcommon import _PWxWidgetBase
from _wxgroupbox import PWxGroupBox

_wxstyles = {
    PANEL_NONE: wx.NO_BORDER,
    PANEL_BOX: wx.SIMPLE_BORDER,
    PANEL_RAISED: wx.RAISED_BORDER,
    PANEL_SUNKEN: wx.SUNKEN_BORDER }

_wxlayouts = {
    LAYOUT_NONE: wx.HORIZONTAL,
    LAYOUT_HORIZONTAL: wx.HORIZONTAL,
    LAYOUT_VERTICAL: wx.VERTICAL }

_wxflags = {
    ALIGN_LEFT: wx.ALIGN_LEFT,
    ALIGN_RIGHT: wx.ALIGN_RIGHT,
    ALIGN_TOP: wx.ALIGN_TOP,
    ALIGN_BOTTOM: wx.ALIGN_BOTTOM }


class PWxPanel(wx.Panel, _PWxWidgetBase, panel.PPanelBase):
    
    def __init__(self, parent,
            layout=LAYOUT_NONE, style=PANEL_NONE, align=ALIGN_JUST,
            margin=-1, spacing=-1, width=-1, height=-1):
        
        wx.Panel.__init__(self, parent, style=_wxstyles[style])
        self._margin = margin
        self._spacing = spacing
        self._expand = True
        self._haswidgets = False
        self._sizer = wx.BoxSizer(_wxlayouts[layout])
        panel.PPanelBase.__init__(self, parent, layout, style, align,
            margin, spacing, width, height)
    
    def _addwidget(self, widget):
        # People say the wxWidgets layout model is simple and easy to use,
        # but comparing this cruft with the Qt or KDE code, I'm not so sure...
        
        if self._haswidgets:
            if self._spacing > -1:
                self._sizer.AddSpacer(self._spacing)
        elif self._margin > -1:
            self._sizer.AddSpacer(self._margin)
        
        if hasattr(widget, '_align') and (widget._align != ALIGN_JUST):
            proportion = 0
            flag = _wxflags[widget._align]
        else:
            proportion = 1
            flag = 0
        
        if hasattr(widget, '_expand') and widget._expand:
            flag |= wx.EXPAND
        
        if self._sizer.GetOrientation() == wx.VERTICAL:
            horiz_pad = self._margin
            vert_pad = -1
            flag |= wx.ALIGN_CENTER_HORIZONTAL
        else:
            horiz_pad = -1
            vert_pad = self._margin
            flag |= wx.ALIGN_CENTER_VERTICAL
        
        if horiz_pad > -1:
            flag |= wx.LEFT | wx.RIGHT
            border = horiz_pad
        elif vert_pad > -1:
            flag |= wx.TOP | wx.BOTTOM
            border = vert_pad
        else:
            border = 0
        
        # At last we can actually do what we came for...
        self._sizer.Add(widget, proportion, flag, border)
        if not self._haswidgets:
            self._haswidgets = True
    
    def _dolayout(self):
        if self._margin > -1:
            self._sizer.AddSpacer(self._margin)
        self.SetSizerAndFit(self._sizer)
    
    def set_min_size(self, width, height):
        curr_w, curr_h = self._sizer.GetMinSize().Get()
        if width < 0:
            width = curr_w
        if height < 0:
            height = curr_h
        self._sizer.SetMinSize((width, height))
    
    def set_box_width(self, width):
        pass # FIXME
    
    def set_margin(self, margin):
        # Margin is dealt with differently in wxWidgets, see above
        pass
    
    def set_spacing(self, spacing):
        # Spacing is dealt with differently in wxWidgets, see above
        pass

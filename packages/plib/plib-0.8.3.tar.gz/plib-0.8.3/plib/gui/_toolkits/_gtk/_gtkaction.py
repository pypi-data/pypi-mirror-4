#!/usr/bin/env python
"""
Module GTKACTION -- Python GTK Action Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI objects for handling user actions.
"""

import pygtk
pygtk.require('2.0')
import gtk
try:
    import gio
except ImportError:
    gio = None

from plib.gui._base import action

from _gtkcommon import _PGtkCommunicator, _PGtkWidgetBase, _gtkstockids

tooltips = gtk.Tooltips()


class PGtkPopup(gtk.Menu):
    """A customized GTK popup menu class.
    """
    
    def __init__(self, mainwidget):
        self.mainwidget = mainwidget
        gtk.Menu.__init__(self)

class PGtkMenu(gtk.MenuBar, _PGtkWidgetBase, action.PMenuBase):
    """A customized GTK menu class.
    """
    
    popupclass = PGtkPopup
    
    def __init__(self, mainwidget):
        gtk.MenuBar.__init__(self)
        action.PMenuBase.__init__(self, mainwidget)
    
    def _add_popup(self, title, popup):
        item = gtk.MenuItem(title.replace('&', ''))
        item.set_submenu(popup)
        self.append(item)
        item.show()
    
    def _add_popup_action(self, act, popup):
        item = act.create_menu_item()
        popup.append(item)
        item.show()

class PGtkToolBar(gtk.Toolbar, _PGtkWidgetBase, action.PToolBarBase):
    """A customized GTK toolbar class.
    """
    
    def __init__(self, mainwidget):
        gtk.Toolbar.__init__(self)
        action.PToolBarBase.__init__(self, mainwidget)
        self.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        if mainwidget.large_icons:
            iconsize = gtk.ICON_SIZE_DIALOG
        else:
            iconsize = gtk.ICON_SIZE_LARGE_TOOLBAR
        try:
            self.set_icon_size(iconsize)
        except DeprecationWarning:
            # FIXME: Why isn't this caught? How can we get rid of this?
            print "Exception caught."
        if mainwidget.show_labels:
            style = gtk.TOOLBAR_BOTH
        else:
            style = gtk.TOOLBAR_ICONS
        self.set_style(style)
        self.set_border_width(0)
    
    def add_action(self, act):
        item = act.create_tool_item()
        # FIXME: Don't understand why this isn't automatically done when
        # we set the action's tooltip in its constructor.
        item.set_tooltip(tooltips, act.get_toolbar_str(act.key))
        self.insert(item, -1)
    
    def add_separator(self):
        self.insert(gtk.SeparatorToolItem(), -1)

class PGtkAction(gtk.Action, _PGtkCommunicator, action.PActionBase):
    """A customized GTK action class.
    """
    
    def __init__(self, key, mainwidget):
        if key in _gtkstockids:
            stock_id = _gtkstockids[key]
        else:
            stock_id = None
        gtk.Action.__init__(self, self.get_toolbar_str(key),
            self.get_toolbar_str(key), self.get_toolbar_str(key), stock_id)
        if (stock_id is None) and (gio is not None):
            # FIXME: How to set icons in earlier gtk versions?
            self.set_gicon(gio.FileIcon(gio.File(self.get_icon_filename(key))))
        action.PActionBase.__init__(self, key, mainwidget)
    
    def enable(self, enabled):
        self.set_sensitive(enabled)

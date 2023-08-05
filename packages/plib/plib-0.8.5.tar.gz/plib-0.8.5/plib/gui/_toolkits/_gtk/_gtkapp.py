#!/usr/bin/env python
"""
Module GTKAPP -- Python GTK Application Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI application objects.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gdk
import gobject

from plib.gui.defs import *
from plib.gui._base import app

from _gtkcommon import _PGtkCommunicator, _gtksignals


class PGtkAboutDialog(app.PAboutDialogBase, gtk.AboutDialog):
    
    attrmap = {
        'name': "set_name",
        'version': "set_version",
        'copyright': "set_copyright",
        'license': "set_license",
        'description': "set_comments", 
        'developers': "set_authors",
        'website': "set_website",
        'icon': "set_logo_from_file" }
    
    def __init__(self, parent):
        gtk.AboutDialog.__init__(self)
        app.PAboutDialogBase.__init__(self, parent)
    
    def set_logo_from_file(self, filename):
        self.set_logo(gtk.gdk.pixbuf_new_from_file(filename))
    
    def display(self):
        self.run()
        self.hide()


def _gtkfiledialog(parent, title, path, filter, action):
    dlg = gtk.FileChooserDialog(title, parent, action)
    if len(path) > 0:
        dlg.set_current_folder(path)
    if len(filter) > 0:
        flt = gtk.FileFilter()
        flt.add_pattern(filter)
        dlg.set_filter(flt)
    result = dlg.run()
    if result == gtk.RESPONSE_OK:
        retval = dlg.get_filename()
    else:
        retval = ""
    dlg.destroy()
    return retval


class _PGtkBaseMixin(gtk.Window, _PGtkCommunicator):
    """Mixin class for Gtk base windows.
    """
    
    # Define closing signal using 'automagic' class field
    
    # Need to define the 'enter' signal for Entry
    __gsignals__ = { _gtksignals[SIGNAL_CLOSING]:
        (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, ()) }
    
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        # 'automagic' signal connection
        self.setup_notify(SIGNAL_QUERYCLOSE, self.delete_event)
    
    def set_caption(self, caption):
        self.set_title(caption)
    
    def _add_widget(self, widget, x=0, y=0):
        # Only allow adding widgets manually if layout exists
        if hasattr(self, 'layout'):
            self.layout.put(widget, x, y)
            widget.show()
    
    def _move_widget(self, widget, x, y):
        # Only allow adding widgets manually if layout exists
        if hasattr(self, 'layout'):
            self.layout.move(widget, x, y)
            self.layout.resize_children()
    
    def _add_client_widget(self, widget):
        if hasattr(widget, '_box'):
            widget = widget._box
        self.vbox.pack_start(widget, True, True, 0)
        widget.show()
    
    def _init_client(self):
        if self.clientwidget is not None:
            self._add_client_widget(self.clientwidget)
        else:
            self.layout = gtk.Layout()
            self._add_client_widget(self.layout)
    
    def _get_w(self):
        return self.get_size()[0]
    w = property(_get_w)
    
    def _show_window(self):
        gtk.Window.show(self)
    
    def _hide_window(self):
        gtk.Window.hide(self)
    
    def sizetoscreen(self, maximized):
        if maximized:
            self.maximize()
        else:
            self.resize(gtk.gdk.screen_width() - self.sizeoffset,
                gtk.gdk.screen_height() - self.sizeoffset)
    
    def sizetoclient(self, clientwidth, clientheight):
        self.set_size_request(clientwidth, clientheight)
    
    def center(self):
        width, height = self.get_size()
        self.move((gtk.gdk.screen_width() - width) / 2,
            (gtk.gdk.screen_height() - height) / 2)
    
    def show_init(self):
        gtk.Window.show(self)
    
    def exit(self):
        # 'automagic' method to fake SIGNAL_QUERYCLOSE when window closes in
        # response to a program signal
        # (wtf isn't this a method in the GTK API?)
        if not self.emit("delete_event", gtk.gdk.Event(gtk.gdk.DELETE)):
            # Send the closing signal
            self.do_notify(SIGNAL_CLOSING)
            self.destroy()
    
    def delete_event(self):
        # 'automagic' method for SIGNAL_QUERYCLOSE
        return not self._canclose()


class PGtkBaseWindow(_PGtkBaseMixin, app.PBaseWindowBase):
    """Customized Gtk base window class.
    """
    
    def __init__(self, parent, cls=None):
        _PGtkBaseMixin.__init__(self)
        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.vbox.show()
        
        app.PBaseWindowBase.__init__(self, parent, cls)
        self._init_client()
    
    def show_init(self):
        app.PBaseWindowBase.show_init(self)
        _PGtkBaseMixin.show_init(self)


class _PGtkMainMixin(_PGtkBaseMixin):
    """Mixin class for GTK top windows and main windows.
    """
    
    aboutdialogclass = PGtkAboutDialog
    
    def __init__(self):
        _PGtkBaseMixin.__init__(self)
        
        # 'automagic' signal connection
        self.setup_notify(SIGNAL_BEFOREQUIT, self.destroy_event)
    
    def set_iconfile(self, iconfile):
        self.set_icon_from_file(iconfile)
    
    def _size_to_settings(self, width, height):
        self.set_size_request(width, height)
    
    def _move_to_settings(self, left, top):
        self.move(left, top)
    
    def _get_current_geometry(self):
        # FIXME: The x, y returned by this are always 0, 0
        # How the fsck am I supposed to find out the window's
        # coordinates on the screen!@#$%^&*
        a = self.allocation
        return a.x, a.y, a.width, a.height
    
    def choose_directory(self, curdir):
        return _gtkfiledialog(self, "Select folder",
            curdir, "", gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
    
    def destroy_event(self):
        # If we're the main window, this is the 'automagic' method for
        # SIGNAL_BEFOREQUIT
        if self.app.mainwin == self:
            self.app.before_quit()
            gtk.main_quit()


class PGtkTopWindow(_PGtkMainMixin, app.PTopWindowBase):
    """Customized Gtk top window class.
    """
    
    def __init__(self, parent, cls=None):
        _PGtkMainMixin.__init__(self)
        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.vbox.show()
        
        app.PTopWindowBase.__init__(self, parent, cls)
        self._init_client()
    
    def show_init(self):
        app.PTopWindowBase.show_init(self)
        _PGtkMainMixin.show_init(self)


class PGtkApplication(app.PApplicationBase, _PGtkCommunicator):
    """Customized GTK application class.
    """
    
    def __init__(self, arglist=[], cls=None, use_mainwindow=False):
        app.PApplicationBase.__init__(self, arglist, cls, use_mainwindow)
        self.mainwin = self.createMainWidget()
    
    def connect(self, signal, target):
        if self.mainwin is not None:
            self.mainwin.connect(signal, target)
    
    def _eventloop(self):
        gtk.main()
    
    def process_events(self):
        gtk.main_iteration(False)

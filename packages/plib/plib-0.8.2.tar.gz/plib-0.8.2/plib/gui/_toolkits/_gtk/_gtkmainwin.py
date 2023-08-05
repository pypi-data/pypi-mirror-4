#!/usr/bin/env python
"""
Module GTKMAINWIN -- Python GTK Main Window Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK GUI main window objects.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gdk

from plib.gui.defs import *
from plib.gui._base import mainwin

from _gtkcommon import _gtkicons, _stockidmap
from _gtkapp import _PGtkMainMixin, _gtkfiledialog
from _gtkaction import PGtkMenu, PGtkToolBar, PGtkAction
from _gtkstatusbar import PGtkStatusBar

_defaultmenuheight = 25


class PGtkMessageBox(mainwin.PMessageBoxBase):
    """Customized GTK message box.
    """
    
    questionmap = {
        answerYes: gtk.RESPONSE_YES,
        answerNo: gtk.RESPONSE_NO,
        answerCancel: gtk.RESPONSE_CANCEL,
        answerOK: gtk.RESPONSE_OK }
    
    # FIXME: Why does the Ok/Cancel message box bail on both Ok *and* Cancel?
    
    def _messagebox(self, type, caption, text,
            button1, button2=None, button3=None):
        
        dlg = gtk.MessageDialog(self._parent, gtk.DIALOG_MODAL,
            _gtkicons[type], gtk.BUTTONS_NONE, text)
        dlg.set_title(caption)
        dlg.add_button(_stockidmap[button1], button1)
        if button2 is not None:
            dlg.add_button(_stockidmap[button2], button2)
        if button3 is not None:
            dlg.add_button(_stockidmap[button3], button3)
        result = dlg.run()
        dlg.destroy()
        return result


class PGtkFileDialog(mainwin.PFileDialogBase):
    
    def openfiledialog(self, path, filter):
        return _gtkfiledialog(self, "Select file to open",
            path, filter, gtk.FILE_CHOOSER_ACTION_OPEN)
    
    def savefiledialog(self, path, filter):
        return _gtkfiledialog(self, "Select file to save",
            path, filter, gtk.FILE_CHOOSER_ACTION_SAVE)


class PGtkMainWindow(_PGtkMainMixin, mainwin.PMainWindowBase):
    """Customized GTK main window class.
    """
    
    menuclass = PGtkMenu
    toolbarclass = PGtkToolBar
    statusbarclass = PGtkStatusBar
    actionclass = PGtkAction
    messageboxclass = PGtkMessageBox
    filedialogclass = PGtkFileDialog
    
    def __init__(self, parent, cls=None):
        _PGtkMainMixin.__init__(self)
        self.framebox = gtk.VBox()
        self.add(self.framebox)
        self.framebox.show()
        
        mainwin.PMainWindowBase.__init__(self, parent, cls)
        
        self._add_frame_widget(self.menu)
        self._add_frame_widget(self.toolbar)
        
        self.scroller = gtk.ScrolledWindow()
        self.scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.vbox = gtk.VBox()
        self.scroller.add_with_viewport(self.vbox)
        self.vbox.show()
        self._add_frame_widget(self.scroller, True)
        self._init_client()
        
        self._add_frame_widget(self.statusbar)
    
    def _add_frame_widget(self, widget, expand=False):
        self.framebox.pack_start(widget, expand, expand, 0)
        widget.show()
    
    def sizetoclient(self, clientwidth, clientheight):
        # GTK doesn't automatically adjust the client area to exclude
        # the menu, toolbar, and other ancillary widgets
        if self.menu is not None:
            menuheight = self.menu.get_size_request()[1]
        else:
            menuheight = 0
        if self.toolbar is not None:
            toolbarheight = self.toolbar.get_size_request()[1]
        else:
            toolbarheight = 0
        if self.statusbar is not None:
            # FIXME: height doesn't get set quite large enough with status bar
            statusbarheight = self.statusbar.get_size_request()[1]
        else:
            statusbarheight = 0
        self.set_size_request(
            clientwidth, clientheight + menuheight + toolbarheight)
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PGtkMainMixin.show_init(self)

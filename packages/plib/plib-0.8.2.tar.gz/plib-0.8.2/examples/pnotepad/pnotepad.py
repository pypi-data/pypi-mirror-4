#!/usr/bin/env python
"""
PNOTEPAD.PY
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A simple plain text editor using the PLIB package.
"""

import sys
import os

from plib import __version__

from plib.stdlib import version

from plib.gui import main as gui
from plib.gui import common
from plib.gui.defs import *


class PNotepad(gui.PMainWindow, gui.PTextFileEditor):
    
    aboutdata = {
        'name': "PNotepad",
        'version': version.version_string(__version__),
        'copyright': "Copyright (C) 2008-2012 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'description': "Plain Text Editor", 
        'developers': ["Peter Donis"],
        'website': "http://www.peterdonis.net",
        'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0],
            "pnotepad.png") }
    
    # FIXME: Add prefsdata to illustrate combined API with ini file
    
    actionflags = [
        ACTION_FILENEW, ACTION_FILEOPEN, ACTION_FILESAVE, ACTION_FILESAVEAS,
        ACTION_EDITUNDO, ACTION_EDITREDO,
        ACTION_EDITCUT, ACTION_EDITCOPY, ACTION_EDITPASTE,
        ACTION_EDITDELETE, ACTION_EDITSELECTALL,
        ACTION_ABOUT, ACTION_ABOUTTOOLKIT, ACTION_EXIT ]
    
    clientwidgetclass = gui.PEditControl
    defaultcaption = "Plain Text Editor"
    placement = (SIZE_MAXIMIZED, MOVE_NONE)
    queryonexit = False
    
    def __init__(self, app):
        gui.PMainWindow.__init__(self, app)
        self.clientwidget.set_background_color(COLOR_WHITE)
        self.clientwidget.set_font("Courier New", 12)
        if len(sys.argv) > 1:
            fname = sys.argv[1]
        else:
            fname = ""
        gui.PTextFileEditor.__init__(self, filename=fname)
        self.editable = True
        
        # Check to make sure everything initialized properly
        assert self.editor is self
        assert self.mainwidget is self
        assert self.control is self.clientwidget
    
    def _gettype(self):
        return "Plain Text"
    
    def _donew(self):
        gui.PTextFileEditor._donew(self)
        self.statusbar.set_text("Editor cleared.")
    
    def _doload(self):
        gui.PTextFileEditor._doload(self)
        self.statusbar.set_text("File data read.")
    
    def _dosave(self):
        gui.PTextFileEditor._dosave(self)
        self.statusbar.set_text("File data written.")


if __name__ == "__main__":
    gui.runapp(PNotepad)

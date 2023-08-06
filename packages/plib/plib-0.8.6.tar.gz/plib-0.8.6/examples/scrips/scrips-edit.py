#!/usr/bin/env python
"""
SCRIPS-EDIT.PY
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Editor for scrips.dat file used to keep track of
prescription refills.
"""

import sys
import os
import datetime

from plib import __version__
from plib.stdlib import version

from plib.gui import main as gui

from plib.gui import defs
from plib.gui import common

import scrips

# Monkeypatch menu and toolbar items
# FIXME: This also changes the "OK" button label in the
# preferences dialog! Need a way to add a new action
# but still have it appear in a desired spot (currently
# adding new actions puts them at the end of the toolbar)

common.set_action_caption(defs.ACTION_OK, "&Submit")
common.set_action_caption(defs.ACTION_REFRESH, "&Refill")


class ScripLabel(gui.PHeaderLabel):
    
    def __init__(self, text, chars, width=-1,
            align=defs.ALIGN_LEFT, readonly=False):
        
        gui.PHeaderLabel.__init__(self, text, width, align, readonly)
        self.chars = chars
    
    def outputlabel(self, index):
        result = self.text
        if index == 0:
            result = "".join(["#", result])
        return result.ljust(self.chars)


# FIXME: Make "headings" a standard class field in PTableMixin?

headings = [
    ScripLabel("Drug", 16, 150),
    ScripLabel("Rx", 12, 100),
    ScripLabel("Last Filled", 16, 100, defs.ALIGN_CENTER),
    ScripLabel("Days", 8, 100, defs.ALIGN_CENTER),
    ScripLabel("Refills Left", 16, 100, defs.ALIGN_CENTER),
    ScripLabel("Submitted", 0, 100) ]


class ScripEditable(scrips.Scrip):
    
    init_name = "<Name>"
    init_rxnum = "<Rx#>"
    init_days = 30
    init_refills = 0
    init_submitted = False
    
    def __init__(self, tokens=None):
        if tokens is None:
            # The default of today's date takes care of the filldate field
            # since there's no init class field for it
            tokens = [str(getattr(self, 'init_%s' % name,
                    datetime.date.today()))
                for name, _ in self.converters]
        scrips.Scrip.__init__(self, tokens)
    
    def submit(self):
        self.submitted = True
    
    def refill(self):
        self.filldate = datetime.date.today()
        self.refills -= 1
        self.submitted = False
    
    def outputline(self):
        return "".join([self[col].ljust(heading.chars)
            for col, heading in enumerate(headings)])


class ScripList(gui.PTableEditor, gui.PTable):
    
    aboutdata = {
        'name': "ScripsEdit",
        'version': version.version_string(__version__),
        'copyright': "Copyright (C) 2008-2012 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'description': "Prescription Editor", 
        'developers': ["Peter Donis"],
        'website': "http://www.peterdonis.net",
        'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0],
            "scrips.png") }
    
    prefsdata = (scrips.inifile, defs.SECTION_GROUPBOX, {
        "email": "E-Mail Fields",
        "email_fromaddr": "From",
        "email_toaddr": "To",
        "email_typestr": "MIME Type",
        "email_charsetstr": "Character Set",
        "email_serverstr": "Server Hostname",
        "email_portnum": "Server Port",
        "email_username": "User Name",
        "email_password": "Password",
        "headers": "E-Mail Headers",
        "headers_dict": "Python Dictionary",
        "pharmacy": "Pharmacy",
        "pharmacy_name": "Name" })
    
    actionflags = [
        defs.ACTION_FILESAVE,
        defs.ACTION_OK, defs.ACTION_REFRESH,
        defs.ACTION_ADD, defs.ACTION_REMOVE,
        defs.ACTION_PREFS,
        defs.ACTION_ABOUT, defs.ACTION_ABOUTTOOLKIT,
        defs.ACTION_EXIT ]
    
    defaultcaption = "Prescription List Editor"
    large_icons = True
    show_labels = True
    placement = (defs.SIZE_CLIENTWRAP, defs.MOVE_CENTER)
    
    def __init__(self, parent):
        gui.PTable.__init__(self, parent, headings)
        if sys.platform == 'darwin':
            fontsize = 16
        else:
            fontsize = 12
        self.set_font("Arial", fontsize)
        self.set_header_font("Arial", fontsize, bold=True)
        gui.PTableEditor.__init__(self,
            data=scrips.scriplist(scripclass=ScripEditable))
        for row in range(len(self)):
            self.setcolors(row)
        self.editable = True
        
        # Check to make sure editor initialized properly
        assert self.mainwidget is self._parent
        assert self.control is self
        
        # Do the rest of the setup for the main widget
        self.mainwidget.statusbar.set_text("Editing prescription info.")
        # Connect main widget actions that won't be connected automatically
        self.mainwidget.connectaction(defs.ACTION_FILESAVE, self.save)
        self.mainwidget.connectaction(defs.ACTION_OK, self.submitscrip)
        self.mainwidget.connectaction(defs.ACTION_REFRESH, self.refillscrip)
        self.mainwidget.connectaction(defs.ACTION_ADD, self.addscrip)
        self.mainwidget.connectaction(defs.ACTION_REMOVE, self.delscrip)
    
    # FIXME: Figure out how to have editor classes automatically detect this
    if hasattr(gui.PTable, 'edit'):
        
        def edit(self, *args):
            # Distinguish between edit method of PTableEditor
            # and edit method of PTable
            if len(args) > 0:
                return gui.PTable.edit(self, *args)
            return gui.PTableEditor.edit(self)
    
    def _dosave(self):
        lines = self.outputlines()
        f = open(scrips.scripsdatfile(), 'w')
        try:
            f.writelines(lines)
        finally:
            f.close()
    
    def setcolors(self, row=None):
        if row is None:
            row = self.current_row()
        scrip = self.data[row]
        if scrip.due():
            if scrip.submitted:
                self.set_row_fgcolor(row, self.default_fgcolor())
            else:
                self.set_row_fgcolor(row, defs.COLOR_RED)
            self.set_row_bkcolor(row, defs.COLOR_YELLOW)
        else:
            self.set_row_fgcolor(row, self.default_fgcolor())
            self.set_row_bkcolor(row, self.default_bkcolor())
    
    _selected_row = None
    
    def updaterow(self, row):
        self.setcolors(row)
        # Hack because some GUI toolkits fire cell selected and table changed
        # events out of sequence (*cough* wx *cough*)
        # FIXME: Figure out a way to have the wx code take care of this
        # (but see comments in wxcommon.py for how hard that's likely to be)
        if row == self._selected_row:
            self.pending = self.data[row].due() and not self.data[row].submitted
    
    def _on_cellselected(self, row, col):
        self._selected_row = row
        self.updaterow(row)
    
    def _on_tablechanged(self, row, col):
        self.updaterow(row)
    
    def _doupdate(self, row):
        self.control[row]._update(self.data[row])
        self.updaterow(row)
        self.modified = True
    
    def submitscrip(self):
        row = self.current_row()
        self.data[row].submit()
        self._doupdate(row)
    
    def refillscrip(self):
        row = self.current_row()
        self.data[row].refill()
        self._doupdate(row)
    
    def set_min_size(self, width, height, from_code=False):
        # FIXME: there should be a way to make this automatic when
        # the main widget is supposed to size to its client
        gui.PTable.set_min_size(self, width, height)
        if from_code: # and sys.platform != 'darwin':
            # FIXME: figure out why wx on OSX throws 'Bus error' on this;
            # it appears to be in the GetSizeTuple call
            self._parent.sizetoclient(width, height)
    
    def addscrip(self):
        self.append(scrips.scripclass())
        self.set_min_size(self.minwidth(), self.minheight(), True)
        self.modified = True
    
    def delscrip(self):
        scripname = self.data[self.current_row()].name
        msg = "Do you really want to delete %s?" % scripname
        if self._parent.messagebox.query2(
                "Delete Prescription", msg) == defs.answerOK:
            del self[self.current_row()]
            self.set_min_size(self.minwidth(), self.minheight(), True)
            self.modified = True
    
    def headerline(self):
        return "".join([heading.outputlabel(index)
            for index, heading in enumerate(headings)])
    
    def outputlines(self):
        return os.linesep.join([self.headerline()] + [scrip.outputline()
            for scrip in self.data])
    
    def canclose(self):
        # Override so we don't flag the pending state here
        return ((not self.modified) or (self.querysave() != defs.answerCancel))


if __name__ == "__main__":
    # We want to wrap our client widget above in a main window,
    # not just a plain top window, hence the keyword argument
    gui.runapp(ScripList, use_mainwindow=True)

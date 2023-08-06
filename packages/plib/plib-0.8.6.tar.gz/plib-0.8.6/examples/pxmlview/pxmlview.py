#!/usr/bin/env python
"""
PXMLVIEW.PY
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A simple read-only XML file viewer using the PLIB package.
"""

import sys
import os

from plib import __version__

from plib.stdlib import version

from plib.xml import classes
from plib.xml import io
from plib.gui import main as gui
from plib.gui.defs import *


class XMLCData(object):
    
    def __init__(self, text):
        self.text = text
    
    def __len__(self):
        # This ensures no further recursion ('leaf' node).
        return 0
    
    def cdata(self):
        return None
    
    def _get_cols(self):
        return [self.text, "CDATA"]
    
    cols = property(_get_cols)


block_elements = ["p"]


class XMLColsTag(classes.BaseElement):
    
    def tagtype(self):
        if self.tag in block_elements:
            return "markup block"
        return "element"
    
    def _get_cols(self):
        return [" ".join([self.tag] + ["%s='%s'" % (key, self.get(key))
            for key in self.keys()]), self.tagtype()]
    
    cols = property(_get_cols)
    
    def cdata(self):
        # Wrap CDATA text up to look like a minimal leaf subnode.
        if (self.text is not None) and (len(self.text) > 0):
            return XMLCData(str(self.text))
        return None


class XMLListViewItem(gui.PListViewItem):
    
    def __init__(self, parent, index, node):
        # Put data in the form that PListViewItem expects to see.
        if (len(node) == 0) and (node.cdata() is not None):
            childlist = [node.cdata()]
        elif not isinstance(node, XMLCData):
            childlist = node
        else:
            childlist = None
        data = (node.cols, childlist)
        gui.PListViewItem.__init__(self, parent, index, data)
        self.expand()


class XMLListView(gui.PListView):
    
    itemclass = XMLListViewItem
    
    def __init__(self, parent, data):
        self._filename = data
        self._xml = io.parseFile(data, elem=XMLColsTag)
        gui.PListView.__init__(self, parent,
            [gui.PHeaderLabel("XML"),
                gui.PHeaderLabel("Node Type", 150, ALIGN_CENTER)],
            [self._xml.getroot()],
            self.current_changed)
        if sys.platform == 'darwin':
            fontsize = 16
        else:
            fontsize = 12
        self.set_font("Arial", fontsize)
        self.set_header_font("Arial", fontsize, bold=True)
    
    def current_changed(self, item):
        self._parent.print_status(item.cols[0])


class XMLTabWidget(gui.PTabWidget):
    
    def __init__(self, parent):
        self._loaded = False
        self._closing = False
        self.mainwin = parent
        if len(sys.argv) > 1:
            filenames = sys.argv[1:]
        else:
            filenames = []
        if not filenames:
            filename = self.get_filename()
            if not filename:
                sys.exit("You must select an XML file to view.")
            filenames.append(filename)
        gui.PTabWidget.__init__(self, parent, None, self.tab_changed)
        for filename in filenames:
            self.add_file(filename)
        parent.connectaction(ACTION_FILEOPEN, self.open_file)
        self._loaded = True
    
    def get_filename(self):
        fname = self.mainwin.getfiledialog()
        if len(fname) > 0:
            return str(fname)
        return ""
    
    def add_file(self, fname):
        widget = XMLListView(self, fname)
        self.append((os.path.basename(fname), widget))
        if self._loaded and (len(self) > 1):
            self.set_current_index(len(self) - 1)
    
    def open_file(self):
        fname = self.get_filename()
        if len(fname) > 0:
            self.add_file(fname)
    
    def tab_changed(self, widget):
        # FIXME: Make the control handle this properly
        if self._loaded and not self._closing:
            # Only fire the event handler after initial data load
            self.print_status(widget._filename)
    
    def print_status(self, text):
        self._parent.statusbar.set_text(text)


class PXMLViewer(gui.PMainWindow):
    
    aboutdata = {
        'name': "PXMLViewer",
        'version': version.version_string(__version__),
        'copyright': "Copyright (C) 2008-2012 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'description': "XML File Viewer", 
        'developers': ["Peter Donis"],
        'website': "http://www.peterdonis.net",
        'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0],
            "pxmlview.png") }
    
    actionflags = [ACTION_FILEOPEN, ACTION_ABOUT, ACTION_ABOUTTOOLKIT,
        ACTION_EXIT]
    
    clientwidgetclass = XMLTabWidget
    defaultcaption = "XML File Viewer"
    large_icons = True
    placement = (SIZE_MAXIMIZED, MOVE_NONE)
    queryonexit = False
    
    # FIXME: Figure out how to mask the tab change event on shutdown so this
    # hack can be removed
    def acceptclose(self):
        result = gui.PMainWindow.acceptclose(self)
        if result:
            self.clientwidget._closing = True
        return result


if __name__ == "__main__":
    gui.runapp(PXMLViewer) # use_mainwindow=True

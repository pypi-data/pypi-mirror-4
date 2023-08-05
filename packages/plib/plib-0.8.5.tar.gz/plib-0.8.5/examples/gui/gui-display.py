#!/usr/bin/env python
"""
GUI-DISPLAY.PY
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A useless demo app that displays all of the available
GUI actions and their associated images.
"""

import sys

from plib import __version__
from plib.stdlib import version

from plib.gui import main as gui
from plib.gui import defs


class GUIDisplayWindow(gui.PMainWindow):
    
    aboutdata = {
        'name': "GUIDisplay",
        'version': "%s on Python %s" % (
            version.version_string(__version__),
            sys.version.split()[0]
        ),
        'copyright': "Copyright (C) 2008-2012 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'description': "GUI Display Demo",
        'developers': ["Peter Donis"],
        'website': "http://www.peterdonis.net" }
    
    actionflags = sorted(getattr(defs, name)
        for name in dir(defs)
        if name.startswith('ACTION_'))
    
    clientwidgetclass = gui.PTextDisplay
    defaultcaption = "GUI Display Demo"
    placement = (defs.SIZE_MAXIMIZED, defs.MOVE_NONE)
    
    def __init__(self, app):
        gui.PMainWindow.__init__(self, app)
        self.clientwidget.set_text("PLIB GUI Display Demo Application.")


def run():
    from plib.stdlib.options import parse_options
    optlist = (
        ("-l", "--large-icons", { 'action': "store_true",
            'dest': "large_icons", 'default': False,
            'help': "Use large toolbar icons" } ),
        ("-s", "--show-labels", { 'action': "store_true",
            'dest': "show_labels", 'default': False,
            'help': "Show toolbar button labels" } ),
        ("-q", "--query-on-exit", { 'action': "store_true",
            'dest': "queryonexit", 'default': False,
            'help': "Ask for confirmation on app exit" } )
        )
    opts, args = parse_options(optlist)
    # The options object supports a dictionary interface,
    # making it easy to update class fields from it
    for opt, value in opts.iteritems():
        setattr(GUIDisplayWindow, opt, value)
    gui.runapp(GUIDisplayWindow)


if __name__ == '__main__':
    run()

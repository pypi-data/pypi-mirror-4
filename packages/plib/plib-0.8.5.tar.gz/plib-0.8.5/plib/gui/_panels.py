#!/usr/bin/env python
"""
Module PANELS -- Dialog Classes for GUI
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines panel classes for use with PLIB.GUI applications.
The following classes are included:

- PMainPanel: adds convenience items to PAutoPanel to
  make it easier to use as the client widget of your GUI
  application's main window.
"""

from plib.gui import main as gui
from plib.gui import specs
from plib.gui.defs import *


class PMainPanel(gui.PAutoPanel):
    """Panel widget specialized to be the client of an app's main window.
    
    This widget will also work in any situation where it is a top-level
    container (e.g., the main panel of a tab in a tab widget).
    """
    
    baseclass = gui.PAutoPanel # so sub-panels will construct properly
    
    align=ALIGN_JUST
    layout = LAYOUT_NONE
    maintitle = None
    margin = specs.framemargin
    spacing = specs.panelspacing
    style=PANEL_NONE
    
    def __init__(self, parent):
        align = self.align
        layout = self.layout
        margin = self.margin
        spacing = self.spacing
        style = self.style
        gui.PAutoPanel.__init__(self, parent, layout=layout, style=style,
            align=align, margin=margin, spacing=spacing)
        
        # Set parent's caption from our maintitle attribute, if defined
        if self.maintitle:
            parent.set_caption(self.maintitle)

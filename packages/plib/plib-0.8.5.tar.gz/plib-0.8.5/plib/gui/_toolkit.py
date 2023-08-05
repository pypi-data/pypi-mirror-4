#!/usr/bin/env python
"""
Internal Module _TOOLKIT
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the code to determine the string
variable ``toolkit`` based on the GUI toolkit being
used. This variable is used in various places in the
GUI library.
"""

from plib.gui.defs import GUI_KDE, GUI_QT, GUI_GTK, GUI_WX, GUI_QT4, GUI_KDE4
from plib.gui._gui import gui_test

if gui_test:
    gui_toolkit = 0
else:
    from plib.gui._gui import gui_toolkit

# Set the toolkit string
# TODO: modularize this so we only need to change one module for a new toolkit

if gui_toolkit == GUI_KDE:
    toolkit = 'KDE'

elif gui_toolkit == GUI_QT:
    toolkit = 'Qt'

elif gui_toolkit == GUI_GTK:
    toolkit = 'Gtk'

elif gui_toolkit == GUI_WX:
    toolkit = 'Wx'

elif gui_toolkit == GUI_QT4:
    toolkit = 'Qt4'

elif gui_toolkit == GUI_KDE4:
    toolkit = 'KDE4'

elif gui_test:
    toolkit = 'Test'

else:
    raise ValueError("No GUI toolkit found; cannot run GUI application.")

del GUI_KDE, GUI_QT, GUI_GTK, GUI_WX, GUI_QT4, GUI_KDE4

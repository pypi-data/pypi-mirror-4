#!/usr/bin/env python
"""
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains a complete GUI application
framework which can wrap any of several GUI toolkits.
The main purpose of the framework is to:

(1) Execute common definitions for GUI objects by choosing
    the appropriate ones for the chosen GUI toolkit;
(2) Provide a few final pieces of common functionality for
    GUI applications.

The overall goal is that GUI applications can simply import the
plib.gui.main module and use its classes without requiring any
knowledge of the GUI toolkit being used, other than allowing the
user to choose it. Choosing a toolkit can be done by setting the
environment variable 'GUI_TOOLKIT' to 1, 2, 3, 4, or 5, to correspond
to the constants defined in plib.gui.defs; alternatively, the
variable can be set to one of the string names 'GUI_QT', 'GUI_KDE',
'GUI_GTK', 'GUI_WX', or 'GUI_QT4', which will then be mapped to their
corresponding values. If no such environment variable is found, or
if its value does not correspond to either of the above possibilities,
various other environment variables and other possibilities are
checked to try to determine whether the script is running under KDE
or Gnome; if KDE, the GUI toolkit defaults to KDE if PyKDE is present,
otherwise Qt; if Gnome, it defaults to GTK. If none of the above is
successful, the toolkit defaults to wxWidgets.

Note that the _setup module is used to determine which toolkits are
installed on the system; since this changes very rarely, one of the
PLIB post-install scripts generates that module so the checking
doesn't have to be done at runtime every time the GUI sub-package
is used.
"""

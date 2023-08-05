#!/usr/bin/env python
"""
SETUP-GUI script for Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script determines what GUI toolkits are present on the system,
and writes a _setup.py module to the plib.gui directory that defines
appropriate constants. This module is then loaded by the main gui module
to determine which toolkits are available for use. The script should be
run after the sub-packages for PLIB are installed, since it uses some of
them.

Note that this script should only need to be run on initial installation
of PLIB or when toolkit packages are installed or uninstalled.
"""

import os

from plib import postinstall

from plib.stdlib.systools import plibpath

print "Determining which GUI toolkits are available..."

# Check which GUI toolkits are available

QT_PRESENT = False
try:
    import qt
except ImportError:
    pass
else:
    QT_PRESENT = True

KDE_PRESENT = False
try:
    import kdecore
except ImportError:
    pass
else:
    KDE_PRESENT = True

GTK_PRESENT = False
try:
    import pygtk
    pygtk.require('2.0')
    import gtk
except ImportError:
    pass
except AssertionError:
    pass
else:
    GTK_PRESENT = True

WX_PRESENT = False
try:
    import wx
except ImportError:
    pass
else:
    WX_PRESENT = True

QT4_PRESENT = False
try:
    from PySide import QtCore
except ImportError:
    try:
        from PyQt4 import Qt
    except ImportError:
        pass
    else:
        QT4_PRESENT = True
else:
    QT4_PRESENT = True

KDE4_PRESENT = False
try:
    from PyKDE4 import kdecore
except ImportError:
    pass
except RuntimeError, e:
    if 'PyQt4.QtCore' in str(e):
        # This will happen if Qt 3 and Qt 4 are both present
        KDE4_PRESENT = True
else:
    KDE4_PRESENT = True

module_vars = ['QT_PRESENT', 'KDE_PRESENT', 'GTK_PRESENT', 'WX_PRESENT',
    'QT4_PRESENT', 'KDE4_PRESENT']
outpath = os.path.join(plibpath, "gui")
outfilename = "_setup.py"
descr = "GUI Toolkit"

postinstall.write_setup_file(__name__, module_vars, outpath, outfilename, descr)

print "PLIB GUI setup done!"

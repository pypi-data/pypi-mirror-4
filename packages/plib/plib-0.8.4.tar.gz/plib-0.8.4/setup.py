#!/usr/bin/python -u
"""
Setup script for PLIB package
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib import __version__ as version

name = "plib"
description = "A namespace package for a number of useful sub-packages and modules."

author = "Peter A. Donis"
author_email = "peterdonis@alum.mit.edu"

startline = 5
endspec = "The Zen of PLIB"

dev_status = "Alpha"

license = "GPLv2"

ext_names = ['plib.stdlib.extensions._extensions']
ext_srcdir = "src"

data_dirs = ["examples"]

classifiers = """
Environment :: Console
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Environment :: X11 Applications :: GTK
Environment :: X11 Applications :: KDE
Environment :: X11 Applications :: Qt
Intended Audience :: Developers
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: Linux
Topic :: Software Development :: Libraries :: Python Modules
"""

post_install = ["%s-setup-%s.py" % (name, s) for s in ("paths", "examples", "gui")]


if __name__ == '__main__':
    import sys
    import os
    from distutils.core import setup
    from setuputils import setup_vars
    setup(**setup_vars(globals()))
    if "install" in sys.argv:
        for scriptname in post_install:
            os.system(scriptname)

#!/usr/bin/env python
"""
PLIB-SETUP-PATHS.PY
Post-install script to determine standard pathnames
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script determines the absolute pathnames for the
following key locations:

-- The main python directory;
-- The PLIB package root directory;
-- The default directory for third-party binaries;
-- The default directory for third-party shared files.

This script only needs to be run on installation of PLIB
or if the python installation directories are changed.
"""

import sys
import os

print "Determining standard pathnames..."

# Path for binaries and scripts (this script should have been installed here)

if os.name == 'posix':
    binpath = os.path.dirname(__file__)

elif os.name == 'nt':
    pythondir = "C:\\Python" + sys.version[:3]
    pythondir = pythondir.replace('.', '')
    binpath = os.path.join(pythondir, "Scripts")

else:
    binpath = ''

# Path for shared files (the plib/examples should have been installed here)

if binpath:
    sharepath = os.path.join(os.path.dirname(binpath), 'share')
    if (not os.path.exists(os.path.join(sharepath, 'plib'))) and (os.path.dirname(binpath) != sys.prefix):
        sharepath = os.path.join(sys.prefix, 'share')
        if not os.path.exists(os.path.join(sharepath, 'plib')):
            raise OSError, "share directory not found!"

else:
    sharepath = ''

# The base Python installation path

if sys.platform == 'win32':
    pythonpath = os.path.join(sys.prefix, 'Lib')

else:
    pythonpath = os.path.join(sys.prefix, 'lib', "python" + sys.version[:3])
    if not os.path.exists(pythonpath):
        pythonpath = pythonpath[:-3]

if not os.path.exists(pythonpath):
    raise OSError, "python directory not found!"

# The root of the PLIB directory tree -- note that this may *not* be the same
# as os.path.join(pythonpath, 'site-packages', 'plib'), depending on which OS
# we're on and what arguments were given to PLIB's setup script

try:
    import plib
    plibpath = os.path.dirname(plib.__file__)
    del plib

except ImportError:
    plibpath = ''
    
    # This could actually happen on OS X depending on how python setup.py install was run
    # (for example, with --prefix=/usr/local but Python is in a framework)
    if (os.path.dirname(binpath) != sys.prefix):
        if pythonpath.endswith(sys.version[:3]):
            testpath = os.path.join(os.path.dirname(binpath), 'lib', 'python' + sys.version[:3],
                'site-packages', 'plib')
        else:
            testpath = os.path.join(os.path.dirname(binpath), 'lib', 'python',
                'site-packages', 'plib')
        if os.path.exists(testpath):
            try:
                # See if we can make plib importable now
                sys.path.insert(0, os.path.dirname(testpath))
                import plib
                del plib
                linked = False
                try:
                    # May not have write permissions here if Python is in the System framework on OS X
                    os.symlink(testpath,
                        os.path.join(pythonpath, 'site-packages', 'plib'))
                    linked = True
                except OSError:
                    if sys.platform == 'darwin':
                        try:
                            os.symlink(testpath,
                                os.path.join('/Library', 'Python', sys.version[:3], 'site-packages', 'plib'))
                            linked = True
                        except OSError:
                            pass
                    else:
                        pass
                if linked:
                    # The symlink should make plib importable without the sys.path munging
                    del sys.path[0]
                    try:
                        import plib
                        del plib
                        plibpath = testpath
                        print "Created symlink of PLIB directory into site-packages..."
                    except ImportError:
                        raise OSError, "symlinking did not make PLIB importable!"
            except ImportError:
                pass

if not plibpath:
    raise OSError, "plib directory not found!"

module_vars = ['pythonpath', 'plibpath', 'binpath', 'sharepath']
outpath = os.path.join(plibpath, 'stdlib')
outfilename = "_paths.py"
descr = "STDLIB Pathname"

from plib import postinstall

postinstall.write_setup_file(__name__, module_vars, outpath, outfilename, descr)

print "PLIB pathname setup done!"

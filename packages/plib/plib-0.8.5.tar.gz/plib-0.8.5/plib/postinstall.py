#!/usr/bin/env python
"""
POSTINSTALL.PY
Post-install script utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common utility routines for the
PLIB post-install scripts.
"""

import sys
import os
import compiler


def write_setup_file(modname, module_vars, outpath, outfilename, descr):
    
    fullpath = os.path.join(outpath, outfilename)
    thismod = sys.modules[modname]
    vars = [(varname, getattr(thismod, varname)) for varname in module_vars]
    for varname, value in vars:
        print "%s: %s" % (varname, value)
    
    print "Writing module %s..." % fullpath
    
    lines = [
        "#!/usr/bin/env python%s" % os.linesep,
        "# %s -- PLIB.%s Setup Module%s" % (outfilename.upper(), descr, os.linesep),
        "# *** This module is automatically generated; do not edit. ***%s" % os.linesep,
        os.linesep ]
    
    for varname, value in vars:
        lines.append('%s = %r%s' % (varname, value, os.linesep))
    
    outfile = open(fullpath, 'w')
    outfile.writelines(lines)
    outfile.close()
    
    print "Byte-compiling %s..." % fullpath
    compiler.compileFile(fullpath)

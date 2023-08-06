#!/usr/bin/env python
"""
Module TerminatorReadWrite
Sub-Package IO.DATA of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the TerminatorReadWrite alternate
data handling class.
"""


class TerminatorReadWrite(object):
    """Data handling class using message terminator byte(s).
    
    Mixin I/O class that looks for a terminator to determine
    when a read is complete and should be processed. Simpler
    than the formatted ``ReadWrite`` class, but more limited
    in usefulness. Strips the terminator from ``self.read_data``
    once detected, and adds the terminator to ``self.write_data``
    before writing it.
    """
    
    overflow = ""
    terminator = "\r\n"
    terminator_received = False
    terminator_written = False
    
    def clear_read(self):
        """Clear current read data.
        
        After clearing, checks for overflow data and puts
        it back into the processing queue if present. Note
        that this method may be called recursively if the
        overflow data contains more than one additional
        "message".
        """
        
        super(TerminatorReadWrite, self).clear_read()
        self.terminator_received = False
        if self.overflow:
            self.read_data = self.overflow
            self.overflow = ""
            self.check_terminator()
        if self.read_complete():
            self.process_data()
            self.clear_read()
    
    def clear_write(self):
        super(TerminatorReadWrite, self).clear_write()
        self.terminator_written = False
    
    def check_terminator(self):
        """Checks for terminator in read data.
        
        Stores away any overflow data temporarily.
        """
        
        if self.terminator in self.read_data:
            self.terminator_received = True
            self.read_data, self.overflow = self.read_data.split(
                self.terminator, 1)
    
    def handle_read(self):
        """Checks incoming data for terminator.
        """
        
        super(TerminatorReadWrite, self).handle_read()
        self.check_terminator()
    
    def read_complete(self):
        return self.terminator_received
    
    def handle_write(self):
        """Adds terminator to the end of each package of written data.
        """
        
        if not self.terminator_written:
            self.write_data += self.terminator
            self.terminator_written = True
        super(TerminatorReadWrite, self).handle_write()

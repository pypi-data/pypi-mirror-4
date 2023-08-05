#!/usr/bin/env python
"""
Module ReadWrite
Sub-Package IO.DATA of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ReadWrite alternate data handling
class.
"""


class ReadWrite(object):
    """Data handling class with initial content length.
    
    Mixin read/write class that converts back and forth
    between simple string data and formatted data that
    has the content length in front. When writing, it
    takes ``self.write_data`` and formats it as below; when
    reading, it assumes the incoming data is formatted
    as below and extracts the content into ``self.read_data``.
    (Note that the ``read_data`` and ``write_data`` fields
    may be clobbered at any time, so data that needs to be
    static should be duplicate stored in another variable.)
    
    Data format: <content-length>\r\n<content>
    """
    
    bufsep = "\r\n"
    bytes_read = 0
    formatted = False
    overflow = ""
    read_len = -1
    
    def clear_read(self):
        """Clear the current read data.
        
        After clearing, checks for overflow data and puts
        it back into the processing queue if present. Note
        that this method may be called recursively if the
        overflow data contains more than one additional
        "message".
        """
        
        super(ReadWrite, self).clear_read()
        self.read_len = -1
        self.bytes_read = 0
        if self.overflow:
            self.read_len, self.read_data = self.unformat_buffer(self.overflow)
            self.overflow = ""
            self.bytes_read = len(self.read_data)
        if self.read_complete():
            self.process_data()
            self.clear_read()
    
    def clear_write(self):
        super(ReadWrite, self).clear_write()
        self.formatted = False
    
    def format_buffer(self, data):
        """Encodes data length at front of data.
        """
        return str(len(data)) + self.bufsep + data
    
    def unformat_buffer(self, data):
        """Splits encoded data into length and content.
        """
        n, received = data.split(self.bufsep, 1)
        return int(n), received
    
    def handle_read(self):
        """Unformats incoming data if content length not extracted.
        """
        
        len_read = len(self.read_data)
        super(ReadWrite, self).handle_read()
        if len(self.read_data) > len_read:
            if (self.read_len < 0) and (self.bufsep in self.read_data):
                self.read_len, received = self.unformat_buffer(self.read_data)
                self.read_data = received
                len_read = 0 # unformatting buffer means we need to reset this
            if self.read_len > -1:
                self.bytes_read += (len(self.read_data) - len_read)
    
    def read_complete(self):
        """Checks for overflow data and stores it away temporarily.
        """
        
        if self.read_len < 0:
            return False
        overflow_len = self.bytes_read - self.read_len
        if overflow_len > 0:
            self.overflow = self.read_data[-overflow_len:]
            self.read_data = self.read_data[:self.read_len]
            self.bytes_read -= overflow_len
        return (self.bytes_read >= self.read_len)
    
    def handle_write(self):
        """Formats data first if not yet formatted.
        """
        
        if not self.formatted:
            self.write_data = self.format_buffer(self.write_data)
            self.formatted = True
        super(ReadWrite, self).handle_write()

#!/usr/bin/env python
"""
Module NET -- Network-Related Utilities
Sub-Package STDLIB of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module is for useful network-related functions. Currently
the only function implemented is ``found_network``, which
takes an IP address prefix (e.g, 192.168.1) and determines
whether any network interface on the machine has an address
with that prefix.
"""

import sys

from plib.stdlib.builtins import first

if sys.platform == 'darwin':
    # OS X makes it hard to parse ifconfig, but we have no choice
    # (the IOCTL stuff we use on Linux isn't there, and we can't
    # rely on socket.gethostname to give us a real IP address either)
    
    from plib.sdtlib.proc import process_output
    
    
    def _entries(s):
        entry = []
        entry_started = False
        for line in s.splitlines():
            if (not entry) or line.startswith('\t'):
                entry.append(line)
            else:
                yield entry
                entry = [line]
    
    
    def _entry_has_network(entry, netprefix):
        return first(line for line in entry if netprefix in line)
    
    
    def found_network(netprefix):
        s = process_output('/sbin/ifconfig')
        if s:
            s = s.strip()
            for entry in _entries(s):
                line = _entry_has_network(entry, netprefix)
                if line:
                    loc = line.find(netprefix)
                    end = line.find(' ', loc)  # space ends the IP address
                    return line[loc:end]
        return None


elif sys.platform.startswith('linux'):
    
    import socket
    import fcntl
    import struct
    import array
    
    
    def _buf_name(buf):
        return buf.split('\0', 1)[0]
    
    
    def _buf_addr(buf):
        return '.'.join(str(ord(buf[j])) for j in xrange(4, 8))
    
    
    def _all_interfaces():
        # This is faster and less prone to breakage than parsing ifconfig
        max_possible = 16  # arbitrary, raise if needed
        bytes = max_possible * 32
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        names = array.array('B', '\0' * bytes)
        outbytes = struct.unpack('iL', fcntl.ioctl(
            s.fileno(),
            0x8912,  # SIOCGIFCONF
            struct.pack('iL', bytes, names.buffer_info()[0]) ))[0]
        namestr = names.tostring()
        return ((_buf_name(namestr[i:i+16]), _buf_addr(namestr[i+16:i+32]))
            for i in range(0, outbytes, 32))
    
    
    def found_network(netprefix):
        return first(ifaddr
            for _, ifaddr in _all_interfaces()
            if ifaddr.startswith(netprefix))


else:  # Win32 and FreeBSD -- strange bedfellows :-)
    
    import socket
    
    
    def found_network(netprefix):
        # It would be nice if we could always use this simple method, but
        # it doesn't appear to work consistently on Linux or OS X (only
        # localhost appears)
        return first(ipaddr
            for ipaddr in socket.gethostbyname_ex(socket.gethostname())[2]
            if ipaddr.startswith(netprefix))

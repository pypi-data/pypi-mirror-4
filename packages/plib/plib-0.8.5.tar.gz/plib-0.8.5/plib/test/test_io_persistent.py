#!/usr/bin/env python
"""
TEST_IO_PERSISTENT.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the persistent async I/O
classes in the PLIB.STDLIB sub-package.
"""

import unittest
import select

from plib.io import async

from io_testlib import PersistentTest
from io_testlib_persistent import ReadWriteTestMixin, TerminatorTestMixin

# Only run these tests if poll is available

if hasattr(select, 'poll'):
    
    async.use_poll(True) # ensure we use poll (not strictly necessary
                         # since True is the default, just shows usage)
    
    
    class XPersistentTest(ReadWriteTestMixin, PersistentTest, unittest.TestCase):
        
        client_list = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
        server_list = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]
    
    
    class XPersistentTestWithPush(XPersistentTest):
        
        test_auto_push = True
    
    
    class XPersistentTestLargeMessage1(XPersistentTest):
        
        client_list = ["a" * 6000, "b" * 6000, "c" * 6000]
        server_list = ["1" * 6000, "2" * 6000, "3" * 6000]
    
    
    class XPersistentTestLargeMessage2(XPersistentTest):
        
        client_list = ["a" * 10000, "b" * 10000, "c" * 10000]
        server_list = ["1" * 10000, "2" * 10000, "3" * 10000]
    
    
    class YPersistentTest(TerminatorTestMixin, PersistentTest, unittest.TestCase):
        
        client_list = ["Python rocks!", "Try it today!", "You'll be glad you did!"]
        server_list = ["You betcha!", "It's *much* better than Perl!", "And don't even *mention* C++!"]
    
    
    class YPersistentTestWithPush(YPersistentTest):
        
        test_auto_push = True
    
    
    class YPersistentTestLargeMessage1(YPersistentTest):
        
        client_list = ["a" * 6000, "b" * 6000, "c" * 6000]
        server_list = ["1" * 6000, "2" * 6000, "3" * 6000]
    
    
    class YPersistentTestLargeMessage2(YPersistentTest):
        
        client_list = ["a" * 10000, "b" * 10000, "c" * 10000]
        server_list = ["1" * 10000, "2" * 10000, "3" * 10000]


if __name__ == '__main__':
    if not hasattr(select, 'poll'):
        print "Poll not available, skipping persistent I/O tests for poll."
    unittest.main()

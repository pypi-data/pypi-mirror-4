#!/usr/bin/env python
"""
TEST_STDLIB.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the PLIB.STDLIB sub-package.
"""

import unittest

from plib.stdlib.decotools import cached_property
from plib.stdlib.strings import fix_newlines, split_string


class CachedPropertyTest(object):
    def __init__(self):
        self.accessed = False
    def test(self):
        self.accessed = True
        return "Test done."
    test = cached_property(test)


class Test_cached_property(unittest.TestCase):
    
    def test_all(self):
        # Initialize
        self.t = CachedPropertyTest()
        self.failUnless(not self.t.accessed)
        
        # First access sets the accessed flag to True
        # and writes the value to the instance dict
        self.assertEqual(self.t.test, "Test done.")
        self.failUnless('test' in self.t.__dict__)
        self.failUnless(self.t.accessed)
        
        # Next access leaves the accessed flag alone
        self.t.accessed = False
        self.assertEqual(self.t.test, "Test done.")
        self.failUnless(not self.t.accessed)
        
        # The cached property can be deleted
        del self.t.test
        self.failUnless(not ('test' in self.t.__dict__))
        
        # And overwritten without triggering it
        self.t.test = "Other value."
        self.assertEqual(self.t.test, "Other value.")
        self.failUnless(not self.t.accessed)
        
        # Deleting re-starts the property
        del self.t.test
        self.assertEqual(self.t.test, "Test done.")
        self.failUnless('test' in self.t.__dict__)
        self.failUnless(self.t.accessed)
        
        # One other wrinkle; hasattr also triggers
        # the property!
        del self.t.test
        self.t.accessed = False
        self.failUnless(hasattr(self.t, 'test'))
        self.failUnless('test' in self.t.__dict__)
        self.failUnless(self.t.accessed)


if __name__ == '__main__':
    unittest.main()

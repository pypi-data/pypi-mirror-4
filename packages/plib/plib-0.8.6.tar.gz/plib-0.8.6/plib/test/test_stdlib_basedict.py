#!/usr/bin/env python
"""
TEST_STDLIB_BASEDICT.PY -- test script for plib.stdlib.basedict
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the basedict class.
"""

import unittest

from plib.stdlib.coll import basedict

import stdlib_mapping_testlib


class testdict(basedict):
    def __init__(self, mapping=None, **kwargs):
        self._storage = {}
        basedict.__init__(self, mapping, **kwargs)
    def _keylist(self):
        return list(self._storage.iterkeys())
    def _get_value(self, key):
        return self._storage[key]
    def _set_value(self, key, value):
        self._storage[key] = value
    def _add_key(self, key, value):
        self._storage[key] = value
    def _del_key(self, key):
        del self._storage[key]


class Test_basedict(stdlib_mapping_testlib.MutableMappingTest):
    type2test = testdict


if __name__ == '__main__':
    unittest.main()

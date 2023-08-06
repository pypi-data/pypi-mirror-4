#!/usr/bin/env python
"""
STDLIB_MAPPING_TESTLIB.PY -- utility module for common 'abstract' mapping object tests
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common code for the 'abstract mapping' types in
plib.stdlib. Code is taken from the mapping_test module in the Python test
package; however, not all of the 'standard' mapping type tests are
implemented, only those which test 'generic' behaviors that are emulated
by the plib classes.
"""

import unittest


class ImmutableMappingTest(unittest.TestCase):
    # The type to be tested
    type2test = None
    
    # Useful helper functions
    def _reference(self):
        # Return a dictionary of values which are invariant by storage
        # in the object under test
        return {1:2, "key1":"value1", "key2":(1,2,3)}
    
    def _empty_mapping(self):
        # Return an empty mapping object
        return self.type2test()
    
    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        
        self.reference = self._reference().copy()
        
        # A (key, value) pair not in the mapping
        key, value = self.reference.popitem()
        self.other = {key:value}
        
        # A (key, value) pair in the mapping
        key, value = self.reference.popitem()
        self.inmapping = {key:value}
        self.reference[key] = value
    
    def test_read(self):
        # Test for read only operations on mapping
        p = self._empty_mapping()
        d = self.type2test(self.reference)
        
        #Indexing
        for key, value in self.reference.items():
            self.assertEqual(d[key], value)
        knownkey = self.other.keys()[0]
        self.failUnlessRaises(KeyError, lambda:d[knownkey])
        
        #len
        self.assertEqual(len(p), 0)
        self.assertEqual(len(d), len(self.reference))
        
        #has_key
        for k in self.reference:
            self.assert_(d.has_key(k))
            self.assert_(k in d)
        for k in self.other:
            self.failIf(d.has_key(k))
            self.failIf(k in d)
        
        #eq, ne
        self.assert_(p == p)
        self.assert_(d == d)
        self.assert_(p != d)
        self.assert_(d != p)
        
        #__non__zero__
        if p: self.fail("Empty mapping must compare to False")
        if not d: self.fail("Full mapping must compare to True")
        
        # iterkeys() ...
        def check_iter(it, ref):
            self.assert_(hasattr(it, 'next'))
            self.assert_(hasattr(it, '__iter__'))
            x = list(it)
            self.assert_(set(x)==set(ref))
        
        check_iter(iter(d), self.reference.keys())
        check_iter(d.iterkeys(), self.reference.keys())
        check_iter(d.itervalues(), self.reference.values())
        check_iter(d.iteritems(), self.reference.items())
        
        #get
        key, value = d.iteritems().next()
        knownkey, knownvalue = self.other.iteritems().next()
        self.assertEqual(d.get(key, knownvalue), value)
        self.assertEqual(d.get(knownkey, knownvalue), knownvalue)
        self.failIf(knownkey in d)
    
    def test_bool(self):
        self.assert_(not self._empty_mapping())
        self.assert_(self.type2test(self.reference))
        self.assert_(bool(self._empty_mapping()) is False)
        self.assert_(bool(self.type2test(self.reference)) is True)
    
    def test_keys(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.iterkeys()), [])
        d = self.type2test(self.reference)
        keys = list(d.iterkeys())
        self.assert_(self.inmapping.keys()[0] in keys)
        self.assert_(self.other.keys()[0] not in keys)
        #self.assertRaises(TypeError, d.keys, None) ??
    
    def test_values(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.itervalues()), [])
        d = self.type2test(self.reference)
        values = list(d.itervalues())
        self.assert_(self.inmapping.values()[0] in values)
        self.assert_(self.other.values()[0] not in values)
        #self.assertRaises(TypeError, d.values, None) ??
    
    def test_items(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.iteritems()), [])
        d = self.type2test(self.reference)
        items = list(d.iteritems())
        self.assert_(self.inmapping.items()[0] in items)
        self.assert_(self.other.items()[0] not in items)
        #self.assertRaises(TypeError, d.items, None) ??
    
    def test_has_key(self):
        d = self._empty_mapping()
        self.assert_(not d.has_key('a'))
        d = self.type2test(self.reference)
        self.assert_(d.has_key(self.inmapping.keys()[0]))
        self.assert_(not d.has_key(self.other.keys()[0]))
    
    def test_contains(self):
        d = self._empty_mapping()
        self.assert_(not ('a' in d))
        self.assert_('a' not in d)
        d = self.type2test(self.reference)
        self.assert_(self.inmapping.keys()[0] in d)
        self.assert_(not (self.other.keys()[0] in d))
        self.assert_(self.other.keys()[0] not in d)
    
    def test_len(self):
        d = self._empty_mapping()
        self.assertEqual(len(d), 0)
        d = self.type2test(self.reference)
        self.assertEqual(len(d), len(self.reference))
    
    def test_getitem(self):
        d = self.type2test(self.reference)
        self.assertEqual(d[self.inmapping.keys()[0]], self.inmapping.values()[0])
        #self.assertRaises(TypeError, d.__getitem__) ??
    
    def test_setitem(self):
        d = self.type2test({'a': 1, 'b': 2})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        
        def test_set(test):
            test['a'] = 4
        
        self.assertRaises(TypeError, test_set, d)
        
        def test_set2(test):
            test['c'] = 3
        
        self.assertRaises(TypeError, test_set2, d)
    
    def test_delitem(self):
        d = self.type2test({'a': 1, 'b': 2})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        
        def test_del(test):
            del test['a']
        
        # Need to catch two exceptions here due to weirdness with
        # Python ABC special method handling
        self.assertRaises((TypeError, AttributeError), test_del, d)
        
        def test_del2(test):
            del test['c']
        
        self.assertRaises((TypeError, AttributeError), test_del2, d)
        #self.assertRaises(TypeError, d.__getitem__) ??
    
    def test_get(self):
        d = self._empty_mapping()
        self.assert_(d.get(self.other.keys()[0]) is None)
        self.assertEqual(d.get(self.other.keys()[0], 3), 3)
        d = self.type2test(self.reference)
        self.assert_(d.get(self.other.keys()[0]) is None)
        self.assertEqual(d.get(self.other.keys()[0], 3), 3)
        self.assertEqual(d.get(self.inmapping.keys()[0]), self.inmapping.values()[0])
        self.assertEqual(d.get(self.inmapping.keys()[0], 3), self.inmapping.values()[0])
        #self.assertRaises(TypeError, d.get) ??
        #self.assertRaises(TypeError, d.get, None, None, None) ??


class FixedKeysMappingTest(ImmutableMappingTest):
    
    def test_bool_fixed(self):
        self.assert_(self.type2test({"x": "y"}))
        self.assert_(bool(self.type2test({"x": "y"})) is True)
    
    def test_keys_fixed(self):
        d = self.type2test({'a': 1, 'b': 2})
        k = list(d.iterkeys())
        self.assert_('a' in k)
        self.assert_('b' in k)
        self.assert_('c' not in k)
    
    def test_values_fixed(self):
        d = self.type2test({1:2})
        self.assertEqual(list(d.itervalues()), [2])
    
    def test_items_fixed(self):
        d = self.type2test({1:2})
        self.assertEqual(list(d.iteritems()), [(1, 2)])
    
    def test_has_key_fixed(self):
        d = self.type2test({'a': 1, 'b': 2})
        k = list(d.iterkeys())
        k.sort()
        self.assertEqual(k, ['a', 'b'])
        #self.assertRaises(TypeError, d.has_key) ??
    
    def test_contains_fixed(self):
        d = self.type2test({'a': 1, 'b': 2})
        self.assert_('a' in d)
        self.assert_('b' in d)
        self.assert_('c' not in d)
        #self.assertRaises(TypeError, d.__contains__) ??
    
    def test_len_fixed(self):
        d = self.type2test({'a': 1, 'b': 2})
        self.assertEqual(len(d), 2)
    
    def test_setitem(self):
        d = self.type2test({'a': 1, 'b': 2})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        self.assertEqual(len(d), 2)
        d['a'] = 4
        self.assertEqual(d['a'], 4)
        self.assertEqual(len(d), 2)
        
        def test_set(test):
            test['c'] = 3
        
        self.assertRaises(KeyError, test_set, d)
    
    def test_get_fixed(self):
        d = self._empty_mapping()
        self.assert_(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        d = self.type2test({'a' : 1, 'b' : 2})
        self.assert_(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)
    
    def test_update(self):
        # mapping argument
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.update, self.other)
        
        # mapping argument
        d = self.type2test({1:1, 2:2, 3:3})
        self.assertEqual(d, {1:1, 2:2, 3:3})
        d.update({1:4, 2:5, 3:6})
        self.assertEqual(d, {1:4, 2:5, 3:6})
        
        # no argument
        d = self._empty_mapping()
        d.update()
        self.assertEqual(d, self._empty_mapping())
        
        # no argument
        d = self.type2test({1:1, 2:2, 3:3})
        l = len(d)
        d.update()
        self.assertEqual(d, {1:1, 2:2, 3:3})
        self.assertEqual(len(d), l)
        
        # keyword arguments
        d = self.type2test({"x":1, "y":2, "z":3})
        self.assertEqual(d, {"x":1, "y":2, "z":3})
        d.update(x=100)
        self.assertEqual(d, {"x":100, "y":2, "z":3})
        d.update(y=20)
        self.assertEqual(d, {"x":100, "y":20, "z":3})
        d.update(z=-3)
        self.assertEqual(d, {"x":100, "y":20, "z":-3})
        d.update(x=1, y=2, z=3)
        self.assertEqual(d, {"x":1, "y":2, "z":3})
        self.assertRaises(KeyError, d.update, d=4)
        
        # item sequence
        d = self.type2test(self.other)
        d.update(self.other.items())
        self.assertEqual(list(d.iteritems()), self.other.items())
        
        # item sequence
        d = self.type2test([("x", 100), ("y", 20)])
        self.assertEqual(d, {"x":100, "y":20})
        
        # both item sequence and keyword arguments
        d = self.type2test({"x":3, "y":4})
        self.assertEqual(d, {"x":3, "y":4})
        d.update([("x", 100), ("y", 20)], x=1, y=2)
        self.assertEqual(d, {"x":1, "y":2})
        
        # iterator
        d = self.type2test({1:2, 3:4, 5:6})
        d.update(self.type2test({1:2, 3:4, 5:6}).iteritems())
        self.assertEqual(d, {1:2, 3:4, 5:6})
        
        # invalid argument
        self.assertRaises((TypeError, AttributeError), d.update, 42)


class MutableMappingTest(FixedKeysMappingTest):
    
    def _full_mapping(self, data):
        # Return mapping filled with data, assuming full mutability
        x = self._empty_mapping()
        for key, value in data.items():
            x[key] = value
        return x
    
    def test_constructor(self):
        self.assertEqual(self._empty_mapping(), self._empty_mapping())
        self.assert_(self._empty_mapping() is not self._empty_mapping())
        self.assertEqual(self.type2test(x=1, y=2), {"x": 1, "y": 2})
    
    def test_bool_full(self):
        self.assert_(self._full_mapping({"x": "y"}))
        self.assert_(bool(self._full_mapping({"x": "y"})) is True)
    
    def test_keys_full(self):
        d = self._full_mapping({'a': 1, 'b': 2})
        k = list(d.iterkeys())
        self.assert_('a' in k)
        self.assert_('b' in k)
        self.assert_('c' not in k)
    
    def test_values_full(self):
        d = self._full_mapping({1:2})
        self.assertEqual(list(d.itervalues()), [2])
    
    def test_items_full(self):
        d = self._full_mapping({1:2})
        self.assertEqual(list(d.iteritems()), [(1, 2)])
    
    def test_has_key_full(self):
        d = self._full_mapping({'a': 1, 'b': 2})
        k = list(d.iterkeys())
        k.sort()
        self.assertEqual(k, ['a', 'b'])
        self.assertRaises(TypeError, d.has_key)
    
    def test_contains_full(self):
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assert_('a' in d)
        self.assert_('b' in d)
        self.assert_('c' not in d)
        self.assertRaises(TypeError, d.__contains__)
    
    def test_len_full(self):
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assertEqual(len(d), 2)
    
    def test_setitem(self):
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        self.assertEqual(len(d), 2)
        d['c'] = 3
        d['a'] = 4
        self.assertEqual(d['c'], 3)
        self.assertEqual(d['b'], 2)
        self.assertEqual(d['a'], 4)
        self.assertEqual(len(d), 3)
    
    def test_delitem(self):
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        self.assertEqual(len(d), 2)
        del d['b']
        self.assertEqual(d, {'a': 1})
        self.assertEqual(len(d), 1)
        
        def test_get(test):
            return test['b']
        
        self.assertRaises(KeyError, test_get, d)
        
        def test_del(test):
            del test['c']
        
        self.assertRaises(KeyError, test_del, d)
    
    def test_get_full(self):
        d = self._empty_mapping()
        self.assert_(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        d = self._full_mapping({'a' : 1, 'b' : 2})
        self.assert_(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)
    
    def test_write(self):
        # Test for write operations on mapping
        p = self._empty_mapping()
        #Indexing
        for key, value in self.reference.items():
            p[key] = value
            self.assertEqual(p[key], value)
        for key in self.reference.keys():
            del p[key]
            self.failUnlessRaises(KeyError, lambda:p[key])
        p = self._empty_mapping()
        #update
        p.update(self.reference)
        self.assertEqual(dict(p), self.reference)
        items = p.items()
        p = self._empty_mapping()
        p.update(items)
        self.assertEqual(dict(p), self.reference)
        d = self._full_mapping(self.reference)
        #setdefault
        key, value = d.iteritems().next()
        knownkey, knownvalue = self.other.iteritems().next()
        self.assertEqual(d.setdefault(key, knownvalue), value)
        self.assertEqual(d[key], value)
        self.assertEqual(d.setdefault(knownkey, knownvalue), knownvalue)
        self.assertEqual(d[knownkey], knownvalue)
        #pop
        self.assertEqual(d.pop(knownkey), knownvalue)
        self.failIf(knownkey in d)
        self.assertRaises(KeyError, d.pop, knownkey)
        default = 909
        d[knownkey] = knownvalue
        self.assertEqual(d.pop(knownkey, default), knownvalue)
        self.failIf(knownkey in d)
        self.assertEqual(d.pop(knownkey, default), default)
        #popitem
        key, value = d.popitem()
        self.failIf(key in d)
        self.assertEqual(value, self.reference[key])
        p=self._empty_mapping()
        self.assertRaises(KeyError, p.popitem)
    
    def test_update(self):
        # mapping argument
        d = self._empty_mapping()
        d.update(self.other)
        self.assertEqual(list(d.iteritems()), self.other.items())
        
        # no argument
        d = self._empty_mapping()
        d.update()
        self.assertEqual(d, self._empty_mapping())
        
        # item sequence
        d = self._empty_mapping()
        d.update(self.other.items())
        self.assertEqual(list(d.iteritems()), self.other.items())
        
        # iterator
        d = self._empty_mapping()
        d.update(self.other.iteritems())
        self.assertEqual(list(d.iteritems()), self.other.items())
        
        # invalid argument
        self.assertRaises((TypeError, AttributeError), d.update, 42)
    
    def test_update_full(self):
        # mapping argument
        d = self._empty_mapping()
        d.update({1:100})
        d.update({2:20})
        d.update({1:1, 2:2, 3:3})
        self.assertEqual(d, {1:1, 2:2, 3:3})
        
        # no argument
        d.update()
        self.assertEqual(d, {1:1, 2:2, 3:3})
        
        # keyword arguments
        d = self._empty_mapping()
        d.update(x=100)
        d.update(y=20)
        d.update(x=1, y=2, z=3)
        self.assertEqual(d, {"x":1, "y":2, "z":3})
        
        # item sequence
        d = self._empty_mapping()
        d.update([("x", 100), ("y", 20)])
        self.assertEqual(d, {"x":100, "y":20})
        
        # both item sequence and keyword arguments
        d = self._empty_mapping()
        d.update([("x", 100), ("y", 20)], x=1, y=2)
        self.assertEqual(d, {"x":1, "y":2})
        
        # iterator
        d = self._full_mapping({1:3, 2:4})
        d.update(self._full_mapping({1:2, 3:4, 5:6}).iteritems())
        self.assertEqual(d, {1:2, 2:4, 3:4, 5:6})
    
    # no test_fromkeys or test_copy as both os.environ and selves don't support it
    
    def test_setdefault(self):
        d = self._empty_mapping()
        self.assertRaises(TypeError, d.setdefault)
    
    def test_setdefault_full(self):
        d = self._empty_mapping()
        self.assert_(d.setdefault('key0') is None)
        d.setdefault('key0', [])
        self.assert_(d.setdefault('key0') is None)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)
    
    def test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)
        self.assertRaises(TypeError, d.popitem, 42)
    
    def test_popitem_full(self):
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(12):
                size = 2**log2size
                a = self._empty_mapping()
                b = self._empty_mapping()
                for i in range(size):
                    a[repr(i)] = i
                    if copymode < 0:
                        b[repr(i)] = i
                if copymode > 0:
                    b = a.copy()
                for i in range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assert_(not(copymode < 0 and ta != tb))
                self.assert_(not a)
                self.assert_(not b)
    
    def test_pop(self):
        d = self._empty_mapping()
        k, v = self.inmapping.items()[0]
        d[k] = v
        self.assertRaises(KeyError, d.pop, self.other.keys()[0])
        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)
        self.assertRaises(KeyError, d.pop, k)
    
    def test_pop_full(self):
        # Tests for pop with specified key
        d = self._empty_mapping()
        k, v = 'abc', 'def'

        # verify longs/ints get same value when key > 32 bits (for 64-bit archs)
        # see SF bug #689659
        x = 4503599627370496L
        y = 4503599627370496
        h = self._full_mapping({x: 'anything', y: 'something else'})
        self.assertEqual(h[x], h[y])

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)
    
    def test_clear(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        d.clear()
        self.assertEqual(d, {})
        self.assertRaises(TypeError, d.clear, None)
    
    def test_fromkeys(self):
        self.assertEqual(self.type2test.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        d = self._empty_mapping()
        self.assert_(not(d.fromkeys('abc') is d))
        self.assertEqual(d.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        self.assertEqual(d.fromkeys((4,5),0), {4:0, 5:0})
        self.assertEqual(d.fromkeys([]), {})
        
        def g():
            yield 1
        
        self.assertEqual(d.fromkeys(g()), {1:None})
        
        self.assertRaises(TypeError, {}.fromkeys, 3)
        
        class dictlike(self.type2test):
            pass
        
        self.assertEqual(dictlike.fromkeys('a'), {'a':None})
        self.assertEqual(dictlike().fromkeys('a'), {'a':None})
        self.assert_(dictlike.fromkeys('a').__class__ is dictlike)
        self.assert_(dictlike().fromkeys('a').__class__ is dictlike)
        self.assert_(type(dictlike.fromkeys('a')) is dictlike)
        
        class Exc(Exception): pass
        
        class baddict1(self.type2test):
            def __init__(self):
                raise Exc()
        
        self.assertRaises(Exc, baddict1.fromkeys, [1])
        
        class BadSeq(object):
            def __iter__(self):
                return self
            def next(self):
                raise Exc()
        
        self.assertRaises(Exc, self.type2test.fromkeys, BadSeq())
        
        class baddict2(self.type2test):
            def __setitem__(self, key, value):
                raise Exc()
        
        self.assertRaises(Exc, baddict2.fromkeys, [1])
    
    def test_copy(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        self.assertEqual(d.copy(), {1:1, 2:2, 3:3})
        d = self._empty_mapping()
        self.assertEqual(d.copy(), d)
        self.assert_(isinstance(d.copy(), d.__class__))
        self.assertRaises(TypeError, d.copy, None)

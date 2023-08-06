#! /usr/bin/env python
"""
Module _MIXINS -- Mixin Classes for PLIB Collections
Sub-Package STDLIB.COLL of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

These mixin classes further specialize the functionality
of the PLIB collection ABCs.
"""

import sys
from abc import ABCMeta, abstractmethod
from itertools import izip

from ._utils import *

__all__ = [
    "AbstractKeyedMixin",
    "AbstractMappingMixin",
    "AbstractDictMixin",
    "AbstractContainerMixin",
    "AbstractSequenceMixin",
    "AbstractListMixin"
]


class AbstractKeyedMixin(object):
    """Mixin class for immutable abstract key-value mapping.
    
    Implements the standard container methods by assuming that
    the object has a list of its valid keys, and knows how to
    retrieve a value for each key; this knowledge should be
    implemented in derived classes in the private ``_keylist``
    and ``_get_value`` methods. Once these two methods are provided,
    the entire immutable mapping interface will work. (Derived
    classes will most likely also need to implement a constructor
    to initially populate the underlying data structure that the
    ``_keylist`` and ``_get_value`` methods access.)
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def _keylist(self):
        """Return container of valid keys for this mapping.
        """
        return []
    
    @abstractmethod
    def _get_value(self, key):
        """Return value corresponding to key.
        
        This method will only be called for keys that are known to
        be in the mapping.
        """
        return None
    
    def __getitem__(self, key):
        if key in self._keylist():
            return self._get_value(key)
        raise KeyError(repr(key))
    
    def __iter__(self):
        return iter(self._keylist())
    
    # We expect this to be faster than the default implementation
    # because _keylist() should be O(1) for length checks
    
    def __len__(self):
        return len(self._keylist())


class AbstractMappingMixin(AbstractKeyedMixin):
    """Mixin class for mapping with fixed keys but mutable values.
    
    Supports key checking on item assignment, enforcing the
    rule that the mapping's set of keys cannot change.
    """
    
    @abstractmethod
    def _set_value(self, key, value):
        """Set value corresponding to key.
        
        This method will only be called for keys that are known to
        be in the mapping.
        """
        pass
    
    def __setitem__(self, key, value):
        if key in self._keylist():
            self._set_value(key, value)
        else:
            raise KeyError(repr(key))


class AbstractDictMixin(AbstractMappingMixin):
    """Mixin class for fully mutable abstract mapping.
    
    Provides default implementations of all mutable mapping methods
    based on the core key/value get/set/add/delete methods.
    """
    
    @abstractmethod
    def _add_key(self, key, value):
        """Add key and value to the mapping.
        
        Will only be called if key is not currently in the mapping.
        """
        pass
    
    @abstractmethod
    def _del_key(self, key):
        """Remove key and its corresponding value from the mapping.
        
        Will only be called if key is currently in the mapping.
        """
        pass
    
    def __setitem__(self, key, value):
        if key in self._keylist():
            self._set_value(key, value)
        else:
            self._add_key(key, value)
    
    def __delitem__(self, key):
        if key in self._keylist():
            self._del_key(key)
        else:
            raise KeyError(repr(key))


class AbstractContainerMixin(object):
    """Mixin class for immutable abstract container.
    
    Support slice operations and normalization of indexes. This class is
    immutable; increasing levels of mutability are provided by
    ``AbstractSequenceMixin`` and ``AbstractListMixin``.
    
    Note that, because this class is immutable and we can't provide a
    constructor without knowing the underlying data storage implementation,
    the slice_class field is provided to allow derived classes to specify
    which class to use when returning slices (e.g., x = s[i:j]). This means
    that these abstract containers are not guaranteed to return slices that
    are of the same type as themselves, although the slice_class should be
    chosen to make them completely compatible functionally.
    """
    
    __metaclass__ = ABCMeta
    
    slice_class = tuple
    
    @abstractmethod
    def _indexlen(self):
        """Return the number of valid indexes into the sequence.
        """
        return 0
    
    @abstractmethod
    def _get_data(self, index):
        """Return a single item by index.
        
        (Slice arguments to ``__getitem__`` may result in multiple calls
        to this method).
        """
        return None
    
    def _index_ok(self, index):
        """Validate, and if necessary normalize, index.
        
        If ``index`` is an int, it must be within the valid sequence
        range (0 to len - 1), after correcting negative indexes relative
        to the end of the sequence. If so, return it; otherwise raise
        ``IndexError``. (The ``normalize`` function is used to accomplish
        this.)
        
        If index is a slice, normalize it (by calling ``normalize_slice``)
        and return a 2-tuple of (slice length, normalize_slice result).
        No exceptions are thrown here for slices; that is left up to
        the caller (since here we don't know whether zero-length slices
        are allowed or not).
        
        Sequences that do not have a known length (e.g., instances of
        the ``IndexedGenerator`` decorator class) will raise ``IndexError``
        if any negative indexes are given, either as single indexes or
        slice elements.
        """
        
        try:
            normlen = self._indexlen()
        except TypeError:
            normlen = None
        if isinstance(index, (int, long)):
            if normlen is None:
                if index < 0:
                    raise IndexError, "sequence index out of range"
                return index
            return normalize(normlen, index)
        elif isinstance(index, slice):
            n = normalize_slice(normlen, index)
            if isinstance(n, (int, long)):
                return (0, n)
            return (len(n), n)
        else:
            raise TypeError, "sequence index must be an integer or a slice"
    
    def __getitem__(self, index):
        index = self._index_ok(index)
        if isinstance(index, tuple):
            length, indexes = index
            if length > 0:
                return self.slice_class(self._get_data(i) for i in indexes)
            return self.slice_class()
        return self._get_data(index)
    
    def __len__(self):
        return self._indexlen()


class AbstractSequenceMixin(AbstractContainerMixin):
    """Mixin class for fixed-length abstract sequence.
    
    Supports argument checking on item assignment, enforcing the
    rule that the sequence's length cannot change.
    """
    
    @abstractmethod
    def _set_data(self, index, value):
        """Store a single item by index.
        
        (Slice arguments to ``__setitem__`` may result in multiple calls
        to this method).
        """
        pass
    
    def __setitem__(self, index, value):
        # NOTE: the treatment of extended slices matches Python 2.6
        # list semantics; that means that, unlike in 2.5 and earlier,
        # extended slices with step == 1 are treated exactly the same
        # as non-extended slices
        extended = isinstance(index, slice) and (index.step is not None) and \
            (index.step != 1)
        index = self._index_ok(index)
        if isinstance(index, tuple):
            if value is self:
                # protect against a[::-1] = a
                value = tuple(value)
            try:
                vlength = len(value)
            except TypeError:
                try:
                    # NOTE: no way to avoid realizing generators/iterators
                    # here; we use tuple because it's faster to construct
                    # than list. As far as I can tell, the Python interpreter
                    # does the same thing for comparing the lengths of values
                    # and slices; the difference is that the interpreter only
                    # does it for extended slices, but we have to do it here
                    # even for a standard slice. This means, of course, that
                    # for fully mutable sequences (like AbstractMixin) and
                    # standard slices, we make an extra copy of the value when
                    # we don't really have to. For the use cases I've had thus
                    # far, this is not a major issue, because I've almost
                    # never had to use slicing, and when I do it's always
                    # small slices; also, typically the overhead of the
                    # individual item inserts (e.g., if each item is a row
                    # in a GUI table or a node in a GUI tree view) is much
                    # higher than the overhead of copying the object pointer
                    # into a tuple. Your mileage may vary.
                    value = tuple(value)
                    vlength = len(value)
                except TypeError:
                    raise TypeError("can only assign an iterable")
            length, index = index
            if (length < 1) and not extended:
                if vlength != 0:
                    self._add_items(index, value)
            elif length != vlength:
                if extended:
                    raise ValueError(
                        "attempt to assign sequence of length %i "
                        "to extended slice of length %i" %
                        (vlength, length))
                self._rep_items(index, value)
            else:
                for i, v in izip(index, value):
                    self._set_data(i, v)
        else:
            self._set_data(index, value)
    
    # These methods allow easy factoring out of the differences
    # between fixed-length and fully mutable sequences
    
    def _add_items(self, index, value):
        raise TypeError("object does not support item insert/append")
    
    def _rep_items(self, indexes, value):
        raise ValueError("object length cannot be changed")
    
    # Alternate implementation of reverse using extended slicing (should
    # be faster than the explicit for loop in abstractsequence.reverse)
    
    def reverse(self):
        l = len(self)
        c = l // 2
        d = l - c
        self[0:c:1], self[l-1:d-1:-1] = self[l-1:d-1:-1], self[0:c:1]


class AbstractListMixin(AbstractSequenceMixin):
    """Mixin class for fully mutable abstract sequence.
    
    Provides default implementations of all mutable sequence methods
    based on the core data get/set/add/delete methods.
    """
    
    slice_class = list
    
    @abstractmethod
    def _add_data(self, index, value):
        """Insert a single item at index.
        
        (Zero-length slice arguments to ``__setitem__`` will result in
        one call to this method for each item in the value being set).
        If index == self.__len__(), this method should append value to
        the sequence.
        """
        pass
    
    @abstractmethod
    def _del_data(self, index):
        """Delete a single item by index.
        
        (Slice arguments to ``__delitem__`` may result in multiple
        calls to this method).
        """
        pass
    
    def _add_items(self, index, value):
        for j, v in enumerate(value):
            self._add_data(index + j, v)
    
    def _del_items(self, indexes):
        # Delete in inverse order to minimize movement of items higher in list
        for i in reversed(indexes):
            self._del_data(i)
    
    def _rep_items(self, indexes, value):
        self._del_items(indexes)
        self._add_items(indexes[0], value)
    
    def __delitem__(self, index):
        index = self._index_ok(index)
        if isinstance(index, tuple):
            length, index = index
            if length > 0:
                self._del_items(index)
        else:
            self._del_data(index)
    
    def insert(self, index, value):
        if not isinstance(index, (int, long)):
            raise TypeError("an integer is required")
        # list.insert is very permissive with index values, match that behavior
        index = min(index, len(self))
        if index < 0:
            index = max(0, len(self) + index)
        self._add_data(index, value)

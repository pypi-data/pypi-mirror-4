#!/usr/bin/env python
"""
Module ITERS -- Tools for Iterators and Generators
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module supplements the ``itertools`` standard library
module. It currently provides the following:

function iterfile --

Returns a generator that can be used in place of "for line in file"
in cases (such as when stdin is the file) where Python's line buffering
might mean the program doesn't get the lines one at a time as they come,
but in bunches. See

http://utcc.utoronto.ca/~cks/space/blog/python/FileIteratorProblems

for a discussion of this issue and the author's code for a function that
fixes it. We use a simpler implementation here because testing has shown
that it is functionally equivalent to the author's.

Note that the issue can also arise, as the blog entry notes,
with line-oriented network protocols, which means any time you are
using a "file-like object" derived from a socket.

function first_n -- generates first n items from iterable

    >>> list(first_n(1, xrange(2)))
    [0]
    >>> list(first_n(2, xrange(2)))
    [0, 1]
    >>> list(first_n(2, xrange(3)))
    [0, 1]
    >>> list(first_n(1, xrange(0)))
    []

function pairwise -- generates items from iterable in pairs

    >>> list(pairwise(xrange(3)))
    [(0, 1), (1, 2)]
    >>> list(pairwise(xrange(2)))
    [(0, 1)]
    >>> list(pairwise(xrange(1)))
    []
    >>> list(pairwise(xrange(0)))
    []

function n_wise -- generates items from iterable in n-tuples; n = 2
is equivalent to pairwise; note that n = 1 converts a list of elements
into a list of 1-tuples; also note that n = 0 raises ValueError

    >>> list(n_wise(3, xrange(4)))
    [(0, 1, 2), (1, 2, 3)]
    >>> list(n_wise(3, xrange(3)))
    [(0, 1, 2)]
    >>> list(n_wise(4, xrange(5)))
    [(0, 1, 2, 3), (1, 2, 3, 4)]
    >>> list(n_wise(4, xrange(4)))
    [(0, 1, 2, 3)]
    >>> list(n_wise(2, xrange(2)))
    [(0, 1)]
    >>> list(n_wise(2, xrange(1)))
    []
    >>> list(n_wise(2, xrange(0)))
    []
    >>> list(n_wise(1, xrange(1)))
    [(0,)]
    >>> list(n_wise(1, xrange(0)))
    []
    >>> list(n_wise(0, xrange(0)))
    Traceback (most recent call last):
    ...
    ValueError: n_wise requires n > 0
    >>> list(n_wise(0, xrange(1)))
    Traceback (most recent call last):
    ...
    ValueError: n_wise requires n > 0

function partitions -- generates all partitions of a sequence or set

    >>> list(partitions(list(xrange(3))))
    [([0], [1, 2]), ([1], [0, 2]), ([2], [0, 1])]

function subsequences -- generates all subsequences of a sequence,
from shortest to longest

    >>> list(subsequences(list(xrange(2))))
    [[0], [1], [0, 1]]
    >>> list(subsequences(list(xrange(3))))
    [[0], [1], [2], [0, 1], [1, 2], [0, 1, 2]]
    >>> list(subsequences(list(xrange(1))))
    [[0]]
    >>> list(subsequences(list(xrange(0))))
    []

function inverse_subsequences -- generates all subsequences of a sequence,
from longest to shortest

    >>> list(inverse_subsequences(list(xrange(3))))
    [[0, 1, 2], [0, 1], [1, 2], [0], [1], [2]]
    >>> list(inverse_subsequences(list(xrange(2))))
    [[0, 1], [0], [1]]
    >>> list(inverse_subsequences(list(xrange(1))))
    [[0]]
    >>> list(inverse_subsequences(list(xrange(0))))
    []

function cyclic_permutations -- generates cyclic permutations of iterable

    >>> list(cyclic_permutations(xrange(3)))
    [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
    >>> list(cyclic_permutations(xrange(2)))
    [(0, 1), (1, 0)]
    >>> list(cyclic_permutations(xrange(1)))
    [(0,)]
    >>> list(cyclic_permutations(xrange(0)))
    []

function unique_permutations -- generates cyclically unique permutations
of iterable with given length r; if r is greater than the length of
iterable, the generator is empty; if r = 0, one empty permutation is
generated (since there is only one 0-length permutation)

    >>> list(unique_permutations(xrange(2), 2))
    [(0, 1)]
    >>> list(unique_permutations(xrange(2), 3))
    []
    >>> list(unique_permutations(xrange(3), 2))
    [(0, 1), (0, 2), (1, 2)]
    >>> list(unique_permutations(xrange(3), 3))
    [(0, 1, 2), (0, 2, 1)]
    >>> list(unique_permutations(xrange(3), 4))
    []
    >>> list(unique_permutations(xrange(3), 1))
    [(0,), (1,), (2,)]
    >>> list(unique_permutations(xrange(2), 1))
    [(0,), (1,)]
    >>> list(unique_permutations(xrange(1), 1))
    [(0,)]
    >>> list(unique_permutations(xrange(1), 2))
    []
    >>> list(unique_permutations(xrange(0), 1))
    []
    >>> list(unique_permutations(xrange(0), 0))
    [()]
    >>> list(unique_permutations(xrange(1), 0))
    [()]
    >>> list(unique_permutations(xrange(2), 0))
    [()]
    >>> list(unique_permutations(xrange(3), 0))
    [()]

function unique_permutations_with_replacement -- generates cyclically
unique permutations of iterable where repeated elements are allowed

    >>> list(unique_permutations_with_replacement(xrange(2), 2))
    [(0, 0), (0, 1), (1, 1)]
    >>> list(unique_permutations_with_replacement(xrange(2), 3))
    [(0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1)]
    >>> list(unique_permutations_with_replacement(xrange(2), 1))
    [(0,), (1,)]
    >>> list(unique_permutations_with_replacement(xrange(1), 1))
    [(0,)]
    >>> list(unique_permutations_with_replacement(xrange(1), 2))
    [(0, 0)]
    >>> list(unique_permutations_with_replacement(xrange(1), 0))
    [()]

function partition -- splits a sequence into multiple sequences at
given index (index must be > 0, otherwise ValueError is raised); if
the ``complete`` argument is ``False``, only partition once

    >>> partition(list(xrange(4)), 2)
    ([0, 1], [2, 3])
    >>> partition(list(xrange(4)), 3)
    ([0, 1, 2], [3])
    >>> partition(list(xrange(4)), 3, fill=True)
    ([0, 1, 2], [3, None, None])
    >>> partition(list(xrange(4)), 4)
    ([0, 1, 2, 3],)
    >>> partition(list(xrange(4)), 4, fill=True)
    ([0, 1, 2, 3],)
    >>> partition(list(xrange(4)), 5)
    ([0, 1, 2, 3],)
    >>> partition(list(xrange(4)), 5, fill=True)
    ([0, 1, 2, 3, None],)
    >>> partition(list(xrange(6)), 2)
    ([0, 1], [2, 3], [4, 5])
    >>> partition(list(xrange(6)), 3)
    ([0, 1, 2], [3, 4, 5])
    >>> partition(list(xrange(6)), 4)
    ([0, 1, 2, 3], [4, 5])
    >>> partition(list(xrange(6)), 5)
    ([0, 1, 2, 3, 4], [5])
    >>> partition(list(xrange(6)), 6)
    ([0, 1, 2, 3, 4, 5],)
    >>> partition(list(xrange(6)), 7)
    ([0, 1, 2, 3, 4, 5],)
    >>> partition(list(xrange(4)), 1)
    ([0], [1], [2], [3])
    >>> partition(list(xrange(1)), 1)
    ([0],)
    >>> partition(list(xrange(1)), 2)
    ([0],)
    >>> partition(list(xrange(1)), 2, fill=True)
    ([0, None],)
    >>> partition(list(xrange(0)), 1)
    ([],)
    >>> partition(list(xrange(0)), 1, fill=True)
    ([],)
    >>> partition(list(xrange(0)), 2)
    ([],)
    >>> partition(list(xrange(0)), 2, fill=True)
    ([],)
    >>> partition(list(xrange(1)), 0)
    Traceback (most recent call last):
    ...
    ValueError: can't partition sequence at index 0
    >>> partition(list(xrange(0)), 0)
    Traceback (most recent call last):
    ...
    ValueError: can't partition sequence at index 0
    >>> partition(list(xrange(3)), 1, complete=False)
    ([0], [1, 2])
    >>> partition(list(xrange(2)), 1, complete=False)
    ([0], [1])
    >>> partition(list(xrange(5)), 2, complete=False)
    ([0, 1], [2, 3, 4])
    >>> partition(list(xrange(4)), 2, complete=False)
    ([0, 1], [2, 3])

function unzip -- inverse of the zip builtin, splits sequence of tuples
into multiple sequences

    >>> unzip(zip(xrange(3), xrange(3)))
    ([0, 1, 2], [0, 1, 2])
    >>> unzip(zip(xrange(3), xrange(3), xrange(3)))
    ([0, 1, 2], [0, 1, 2], [0, 1, 2])
    >>> unzip(zip(xrange(1), xrange(1)))
    ([0], [0])
    >>> unzip(zip(xrange(0), xrange(0)))
    ()
    >>> unzip(xrange(1))
    Traceback (most recent call last):
     ...
    TypeError: zip argument #1 must support iteration

function group_into -- Generate tuples of every n elements of iterable

    >>> list(group_into(2, xrange(10)))
    [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]
    >>> list(group_into(3, xrange(10)))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    >>> list(group_into(3, xrange(10), include_tail=True))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]
    >>> list(group_into(3, xrange(10), include_tail=True, fill_tail=True))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, None, None)]
    >>> list(group_into(1, xrange(2)))
    [(0,), (1,)]
    >>> list(group_into(1, xrange(1)))
    [(0,)]
    >>> list(group_into(2, xrange(1)))
    []
    >>> list(group_into(2, xrange(1), include_tail=True))
    [(0,)]
    >>> list(group_into(2, xrange(1), include_tail=True, fill_tail=True, fillvalue=-1))
    [(0, -1)]
    >>> list(group_into(2, xrange(1), raise_if_tail=True))
    Traceback (most recent call last):
     ...
    ValueError: extra terms in grouped iterable
    >>> list(group_into(0, xrange(1)))
    Traceback (most recent call last):
     ...
    ValueError: can't group iterable into 0-element tuples
    >>> list(group_into(1, xrange(0)))
    []
    >>> list(group_into(1, xrange(0), include_tail=True))
    []
    >>> list(group_into(1, xrange(0), include_tail=True, fill_tail=True))
    []

function exrange -- version of xrange builtin that works with longs

    >>> list(exrange(2147483647, 2147483649))
    [2147483647, 2147483648L]
    >>> list(exrange(2147483647, 2147483651, 2))
    [2147483647, 2147483649L]
    >>> list(exrange(2147483647, 2147483649, 0))
    Traceback (most recent call last):
     ...
    ValueError: exrange() arg 3 must not be zero

function inverse_index -- index of item counting from end of sequence

    >>> inverse_index(list(xrange(3)), 0)
    2
    >>> inverse_index(list(xrange(3)), 1)
    1
    >>> inverse_index(list(xrange(3)), 2)
    0
    >>> inverse_index(list(xrange(3)), 3)
    Traceback (most recent call last):
     ...
    ValueError: 3 is not in list

function is_subsequence -- tests if one sequence is subsequence of another

    >>> is_subsequence(list(xrange(2)), list(xrange(3)))
    True
    >>> is_subsequence(list(xrange(3)), list(xrange(1, 3)))
    False
    >>> is_subsequence(list(xrange(1, 2)), list(xrange(1, 3)))
    True
    >>> is_subsequence(list(xrange(1)), list(xrange(2)))
    True
    >>> is_subsequence(list(xrange(1)), list(xrange(1, 2)))
    False
    >>> is_subsequence(list(xrange(0)), list(xrange(1)))
    True
    >>> is_subsequence(list(xrange(0)), list(xrange(0)))
    True
    >>> is_subsequence(list(xrange(3)), list(xrange(2)))
    False
    >>> is_subsequence(list(xrange(1)), list(xrange(0)))
    False

function count_matches -- returns mapping of unique elements in sequence
to number of times they appear

    >>> sorted(count_matches(list(xrange(1))).iteritems())
    [(0, 1)]
    >>> sorted(count_matches(list(xrange(2))).iteritems())
    [(0, 1), (1, 1)]
    >>> sorted(count_matches(list(xrange(2)) * 2).iteritems())
    [(0, 2), (1, 2)]
    >>> sorted(count_matches(list(xrange(2)) * 2 + [1]).iteritems())
    [(0, 2), (1, 3)]
    >>> sorted(count_matches(list(xrange(2)) * 2 + [2]).iteritems())
    [(0, 2), (1, 2), (2, 1)]
    >>> sorted(count_matches(list(xrange(0))).iteritems())
    []
    >>> sorted(count_matches('abracadabra').iteritems())
    [('a', 5), ('b', 2), ('c', 1), ('d', 1), ('r', 2)]

function sorted_unzip -- returns two sequences from mapping, of keys and
values, in corresponding order, sorted by key or value

    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in xrange(5)))
    ([0, 1, 2, 3, 4], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in xrange(5)), by_value=True)
    ([0, 1, 2, 3, 4], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in xrange(5)), reverse=True)
    ([4, 3, 2, 1, 0], ['e', 'd', 'c', 'b', 'a'])
    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in xrange(5)), by_value=True, reverse=True)
    ([4, 3, 2, 1, 0], ['e', 'd', 'c', 'b', 'a'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in xrange(5)))
    ([0, 1, 2, 3, 4], ['e', 'd', 'c', 'b', 'a'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in xrange(5)), by_value=True)
    ([4, 3, 2, 1, 0], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in xrange(5)), reverse=True)
    ([4, 3, 2, 1, 0], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in xrange(5)), by_value=True, reverse=True)
    ([0, 1, 2, 3, 4], ['e', 'd', 'c', 'b', 'a'])

    >>> list(prefixed_items(['a_1', 'a_2', 'b_3', 'c_4', 'a_5', 'd_6'], 'a_'))
    ['1', '2', '5']
    >>> list(prefixed_items(['a_1', 'a_2', 'b_3', 'c_4', 'a_5', 'd_6'], 'a_', full=True))
    ['a_1', 'a_2', 'a_5']
    >>> list(suffixed_items(['a_1', 'a_2', 'b_1', 'c_2', 'a_3', 'd_4'], '_2'))
    ['a', 'c']
    >>> list(suffixed_items(['a_1', 'a_2', 'b_1', 'c_2', 'a_3', 'd_4'], '_2', full=True))
    ['a_2', 'c_2']
    >>> list(prefixed_items(['a', 'b', 'c'], ''))
    ['a', 'b', 'c']
    >>> list(prefixed_items(['a', 'b', 'c'], '', full=True))
    ['a', 'b', 'c']
    >>> list(suffixed_items(['a', 'b', 'c'], ''))
    ['a', 'b', 'c']
    >>> list(suffixed_items(['a', 'b', 'c'], '', full=True))
    ['a', 'b', 'c']
    >>> list(prefixed_items(['b', 'c'], 'a'))
    []
    >>> list(prefixed_items(['b', 'c'], 'a', full=True))
    []
    >>> list(suffixed_items(['b', 'c'], 'a'))
    []
    >>> list(suffixed_items(['b', 'c'], 'a', full=True))
    []
    >>> list(prefixed_items([], 'a'))
    []
    >>> list(prefixed_items([], 'a', full=True))
    []
    >>> list(suffixed_items([], 'a'))
    []
    >>> list(suffixed_items([], 'a', full=True))
    []
    >>> list(prefixed_items([], ''))
    []
    >>> list(prefixed_items([], '', full=True))
    []
    >>> list(suffixed_items([], ''))
    []
    >>> list(suffixed_items([], '', full=True))
    []

"""

import sys
from itertools import (combinations, combinations_with_replacement,
    islice, izip, izip_longest, permutations, takewhile, tee)
from operator import lt, gt


# File iterator utility

def iterfile(f):
    """Return a generator that yields lines from a file.
    
    This works like "for line in file" does, but avoids potential
    problems with buffering. Use as::
    
        for line in iterfile(file):
    """
    return iter(f.readline, '')


# Iterable functions

def first_n(n, iterable):
    # More intuitive spelling for this usage of islice
    return islice(iterable, n)


def pairwise(iterable):
    # s -> (s0,s1), (s1,s2), (s2, s3), ...
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def n_wise(n, iterable):
    # Return items from iterable in groups of n
    if n <= 0:
        raise ValueError, "n_wise requires n > 0"
    iters = []
    a = iterable
    for _ in xrange(n - 1):
        a, b = tee(a)
        iters.append(a)
        next(b, None)
        a = b  # this makes sure append(a) below gets the right iterable
    iters.append(a)  # this takes care of the n = 1 case as well
    return izip(*iters)


def partitions(s):
    # Generate all pairs of non-empty subsets that partition s
    itemcount = len(s)
    for n in xrange(1, (itemcount / 2) + 1):
        for indexes in combinations(xrange(itemcount), n):
            p = [s[i] for i in indexes]
            o = [s[j] for j in xrange(itemcount) if j not in indexes]
            yield p, o


def _subseq(sequence, step=0):
    length = len(sequence)
    indexes = (0, length)
    start = indexes[step] + 1 + step
    stop = indexes[1 + step] + 1 + step
    step = step or 1
    for current in xrange(start, stop, step):
        for i in xrange(length - current + 1):
            yield sequence[i:i + current]


def subsequences(sequence):
    # Generate all subsequences of sequence, starting with
    # the shortest and ending with the sequence itself
    return _subseq(sequence)


def inverse_subsequences(sequence):
    # Generate all subsequences of sequence, starting with
    # the longest (which is just the sequence itself)
    return _subseq(sequence, -1)


def cyclic_permutations(iterable):
    # Generate just the cyclic permutations of iterable
    # (all permutations are the same length as iterable)
    # cyclic_permutations('123') -> '123', '231', '312'
    pool = tuple(iterable)
    seen = {}  # FIXME: get rid of this?
    r = len(pool)
    s = pool + pool
    for i in xrange(r):
        p = s[i:i + r]
        if p not in seen:
            seen[p] = p
            yield p


def unique_permutations(iterable, r):
    # Generate all cyclically unique r-length permutations of iterable
    pool = tuple(iterable)
    seen = {}  # FIXME: get rid of this?
    for c in combinations(pool, r):
        car, cdr = c[:1], c[1:]
        for p in permutations(cdr):
            u = car + p
            if u not in seen:
                for t in cyclic_permutations(u):
                    seen[t] = u
                yield u


def unique_permutations_with_replacement(iterable, r):
    # Generate all cyclically unique r-length permutations of iterable,
    # where elements can be repeated
    pool = tuple(iterable)
    seen = {}  # FIXME: get rid of this?
    s = len(pool)
    for i in xrange(min(r, s) + 1):
        for c in combinations(pool, i):
            for p in combinations_with_replacement(pool, r - i):
                for u in unique_permutations(c + p, r):
                    if u not in seen:
                        for t in cyclic_permutations(u):
                            seen[t] = u
                        yield u


def partition(iterable, at, complete=True, fill=False, fillvalue=None):
    # Return a tuple of one or more sequences, split from iterable at
    # given index (if there are fewer elements in iterable, then a
    # 1-element tuple containing a sequence of all elements is returned).
    # If complete is True and seq is longer than 2 * at, partition
    # multiple times, and fill in the final element if fill is True,
    # similar to group_into; otherwise only partition once (i.e., into
    # two sequences)
    if at <= 0:
        raise ValueError, "can't partition sequence at index 0"
    if complete:
        results = tuple(list(g) for g in group_into(at, iterable,
            include_tail=True, fill_tail=fill, fillvalue=fillvalue))
        if results:
            return results
        return ([],)
    it = iter(iterable)
    part = list(islice(it, at))
    rest = list(it)
    if not rest:
        return (part,)
    return (part, rest)


def unzip(iterable):
    # Unzip iterable into multiple sequences; assumes iterable
    # contains tuples that are all of the same length.
    return tuple(map(list, zip(*iterable)))


def group_into(n, iterable, include_tail=False, fill_tail=False,
               fillvalue=None, raise_if_tail=False):
    # Return tuples of every n elements of iterable
    # If include_tail is True, yield a last tuple of less than n
    # elements from iterable if present, filled out with fillvalue
    # if fill_tail is True; otherwise, if raise_if_tail is True,
    # raise ValueError if extra elements are present
    if n < 1:
        raise ValueError, "can't group iterable into 0-element tuples"
    args = [iter(iterable)] * n
    sentinel = object()
    for group in izip_longest(*args, fillvalue=sentinel):
        if group[-1] is not sentinel:
            yield group
        elif include_tail:
            tail = tuple(takewhile(lambda g: g is not sentinel, group))
            if fill_tail:
                tail += (fillvalue,) * (n - len(tail))
            yield tail
        elif raise_if_tail:
            raise ValueError, "extra terms in grouped iterable"


def exrange(start, stop, step=1):
    # xrange that works with Python long ints
    if step == 0:
        raise ValueError, "exrange() arg 3 must not be zero"
    if step < 0:
        cmpfn = gt
    else:
        cmpfn = lt
    i = start
    while cmpfn(i, stop):
        yield i
        i += step


# Test and count functions

def inverse_index(seq, elem):
    # Return inverse index of elem in seq (i.e., first element
    # of seq has highest index, down to 0 for last element)
    return len(seq) - seq.index(elem) - 1


def is_subsequence(s, seq):
    # Test if s is a subsequence of seq
    slen = len(s)
    for i in xrange(len(seq) - slen + 1):
        if s == seq[i:i + slen]:
            return True
    return False


# Mapping <=> sequence functions

def count_matches(seq):
    # Return dict of unique elements in seq vs. number of times they appear
    # Assumes all sequence elements are hashable
    results = {}
    for item in seq:
        results.setdefault(item, []).append(True)
    return dict((k, len(v)) for k, v in results.iteritems())


def sorted_unzip(mapping, by_value=False, reverse=False):
    # Return list of keys and list of values from mapping, both
    # sorted in corresponding order, by values if by_value is
    # True, by keys otherwise; reverse parameter governs the sort
    if by_value:
        unsorted_result = ((v, k) for k, v in mapping.iteritems())
    else:
        unsorted_result = mapping.iteritems()
    result = sorted(unsorted_result, reverse=reverse)
    r1, r2 = unzip(result)
    if by_value:
        return r2, r1
    return r1, r2


# Functions on iterables of strings

def prefixed_items(iterable, prefix, full=False):
    """Return items from iterable that start with prefix.
    
    The ``full`` argument controls whether the prefix itself is included
    in the returned items; the default is not to do so.
    
    Note that a zero-length prefix will result in every item of ``iterable``
    being yielded unchanged.
    """
    start = (len(prefix), 0)[full]
    return (item[start:] for item in iterable if item.startswith(prefix))


def suffixed_items(iterable, suffix, full=False):
    """Return items from iterable that end with suffix.
    
    The ``full`` argument controls whether the suffix itself is included
    in the returned items; the default is not to do so.
    
    Note that Python's indexing semantics make this case a bit different from
    the prefix case; item[:-0] doesn't have the corresponding effect to item[0:].
    Also we have to put the ``or None`` check in to allow for a zero-length
    suffix (which should result in every item in the iterable being yielded
    unchanged, as with ``prefixed_items`` above).
    """
    i = slice((-len(suffix) or None, None)[full])
    return (item[i] for item in iterable if item.endswith(suffix))


if __name__ == '__main__':
    import doctest
    doctest.testmod()

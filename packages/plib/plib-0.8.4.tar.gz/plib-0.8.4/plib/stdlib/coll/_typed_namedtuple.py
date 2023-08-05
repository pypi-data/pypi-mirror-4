#! /usr/bin/env python
"""
Module _TYPED_NAMEDTUPLE -- Tuple with named, typed fields
Sub-Package STDLIB.COLL of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Based on the ActiveState recipe at

http://code.activestate.com/recipes/500261/

but with type checking of arguments added.
"""

from operator import itemgetter as _itemgetter
from keyword import iskeyword as _iskeyword
import sys as _sys

from plib.stdlib.iters import group_into as _group_into
from plib.stdlib.builtins import type_from_name as _type_from_name


def typed_namedtuple(typename, fieldspecs, verbose=False):
    """Returns a new subclass of tuple with named, typed fields.
    
    >>> Point = typed_namedtuple('Point', 'x int, y int')
    >>> Point.__doc__        # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)  # instantiate with positional args or keywords
    >>> p[0] + p[1]          # indexable like a plain tuple
    33
    >>> x, y = p             # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y            # fields also accessible by name
    33
    >>> d = p._asdict()      # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)           # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)    # like str.replace() but targets named fields
    Point(x=100, y=22)
    >>> p = Point(11, '22')  # type conversion done on arguments
    >>> x, y = p
    >>> x, y
    (11, 22)
    >>> p = Point(11, 'x')   # invalid arguments raise exception
    Traceback (most recent call last):
     ...
    ValueError: invalid literal for int() with base 10: 'x'
    """
    
    # Parse and validate the field names. Validation serves two purposes,
    # generating informative error messages and preventing template
    # injection attacks.
    
    if isinstance(fieldspecs, basestring):
        # Names and types separated by whitespace and/or commas
        fieldspecs = fieldspecs.replace(',', ' ').split()
    if not isinstance(fieldspecs[0], tuple):
        # Format name, type pairs into tuples
        fieldspecs = list(_group_into(2, fieldspecs))
    field_names = tuple(map(str, [str(spec[0]) for spec in fieldspecs]))
    field_types = tuple(map(_type_from_name, [spec[1] for spec in fieldspecs]))
    for name in (typename,) + field_names:
        if not min(c.isalnum() or c=='_' for c in name):
            raise ValueError(
                'Type and field names must be valid identifiers: %r' % name)
        if _iskeyword(name):
            raise ValueError(
                'Type and field names cannot be keywords: %r' % name)
        if name[0].isdigit():
            raise ValueError(
                'Type and field names must be valid identifiers: %r' % name)
    seen_names = set()
    for name in field_names:
        if name.startswith('_'):
            raise ValueError(
                'Field names cannot start with an underscore: %r' % name)
        if name in seen_names:
            raise ValueError(
                'Encountered duplicate field name: %r' % name)
        seen_names.add(name)
    
    # Create the typecast function template
    typecast_template = '''def typecast(*args):
        return _tuple(_field_types[i](item) for i, item in _enumerate(args)) \n\n'''
    
    # Execute the function template in a temporary namespace
    typecast_namespace = dict(_tuple=tuple, _enumerate=enumerate,
                     _field_types=field_types)
    try:
        exec typecast_template in typecast_namespace
    except SyntaxError, e:
        raise SyntaxError(e.message + ':\n' + typecast_template)
    typecast = typecast_namespace['typecast']
    
    # Create and fill-in the class template
    numfields = len(field_names)
    # Tuple repr without parens or quotes
    argtxt = repr(field_names).replace("'", "")[1:-1]
    reprtxt = ', '.join('%s=%%r' % name for name in field_names)
    template = '''class %(typename)s(tuple):
        '%(typename)s(%(argtxt)s)' \n
        __slots__ = () \n
        _fields = %(field_names)r \n
        def __new__(_cls, %(argtxt)s):
            return _tuple.__new__(_cls, _typecast(%(argtxt)s)) \n
        @classmethod
        def _make(cls, iterable, new=tuple.__new__, len=len):
            'Make a new %(typename)s object from a sequence or iterable'
            result = new(cls, iterable)
            if len(result) != %(numfields)d:
                raise TypeError('Expected %(numfields)d arguments, got %%d' %% len(result))
            return result \n
        def __repr__(self):
            return '%(typename)s(%(reprtxt)s)' %% self \n
        def _asdict(self):
            'Return a new dict which maps field names to their values'
            return dict(zip(self._fields, self)) \n
        def _replace(_self, **kwds):
            'Return a new %(typename)s object replacing specified fields with new values'
            result = _self._make(map(kwds.pop, %(field_names)r, _self))
            if kwds:
                raise ValueError('Got unexpected field names: %%r' %% kwds.keys())
            return result \n
        def __getnewargs__(self):
            return tuple(self) \n\n''' % locals()
    for i, name in enumerate(field_names):
        template += '        %s = _property(_itemgetter(%d))\n' % (name, i)
    if verbose:
        print template
    
    # Execute the template string in a temporary namespace
    namespace = dict(_itemgetter=_itemgetter,
                     __name__='typed_namedtuple_%s' % typename,
                     _property=property, _tuple=tuple,
                     _typecast=typecast)
    try:
        exec template in namespace
    except SyntaxError, e:
        raise SyntaxError(e.message + ':\n' + template)
    result = namespace[typename]
    
    # For pickling to work, the __module__ variable needs to be set to the
    # frame where the named tuple is created.  Bypass this step in enviroments
    # where sys._getframe is not defined (Jython for example) or sys._getframe
    # is not defined for arguments greater than 0 (IronPython).
    try:
        result.__module__ = _sys._getframe(1).f_globals.get(
            '__name__', '__main__')
    except (AttributeError, ValueError):
        pass
    
    return result


if __name__ == '__main__':
    # Determine whether to print out the template string
    # on the first invocation, and the output from the
    # other demonstrations. Note that this is separate
    # from making doctest give verbose output.
    from sys import argv as _argv
    verbose = ('-p' in _argv)
    
    # verify that namedtuple instances can be pickled
    from cPickle import loads, dumps
    Point = typed_namedtuple('Point', 'x int, y int', verbose=verbose)
    p = Point(x=10, y=20)
    assert p == loads(dumps(p, -1))
    
    # test and demonstrate ability to override methods
    class Point(typed_namedtuple('Point', 'x int, y int')):
        @property
        def hypot(self):
            return (self.x ** 2 + self.y ** 2) ** 0.5
        def __str__(self):
            return 'Point: x=%6.3f y=%6.3f hypot=%6.3f' % (
                self.x, self.y, self.hypot)
    
    for p in Point(3,4), Point(14,5), Point(9./7,6):
        if verbose:
            print p
    
    class Point(typed_namedtuple('Point', 'x int, y int')):
        'Point class with optimized _make() and _replace() without error-checking'
        _make = classmethod(tuple.__new__)
        def _replace(self, _map=map, **kwds):
            return self._make(_map(kwds.get, ('x', 'y'), self))
    
    _output = Point(11, 22)._replace(x=100)
    if verbose:
        print _output
    
    import doctest
    results = doctest.testmod()
    if verbose:
        TestResults = typed_namedtuple('TestResults', 'failed int, attempted int')
        print TestResults(*results)

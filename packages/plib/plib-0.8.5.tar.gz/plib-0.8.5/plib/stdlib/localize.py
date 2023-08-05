#!/usr/bin/env python
"""
Module LOCALIZE -- PLIB Localization Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains useful localization functions that
should be in the standard library but aren't. :p

Sanity checks since the functions taking ``datetime``
arguments use a different API:

    >>> from datetime import datetime
    >>> dt = datetime.now()
    >>> assert weekdayname(dt.weekday(), dt=True) == dt_weekdayname(dt)
    >>> assert weekdayname_long(dt.weekday(), dt=True) == dt_weekdayname_long(dt)
    >>> assert monthname(dt.month) == dt_monthname(dt)
    >>> assert monthname_long(dt.month) == dt_monthname_long(dt)
"""

import locale
from locale import nl_langinfo


weekdays = iso_weekdays = set([1, 2, 3, 4, 5, 6, 7])
dt_weekdays = set([0, 1, 2, 3, 4, 5, 6])


def _convert_weekday(weekday, dt, iso):
    if iso:
        if weekday not in iso_weekdays:
            raise ValueError("{} is not a valid ISO weekday number".format(weekday))
    elif dt:
        if weekday not in dt_weekdays:
            raise ValueError("{} is not a valid datetime weekday number".format(weekday))
    else:
        if weekday not in weekdays:
            raise ValueError("{} is not a valid weekday number".format(weekday))
    return (
        weekday % 7 + 1 if iso else
        (weekday + 1) % 7 + 1 if dt else
        weekday
    )


def weekdayname(weekday, dt=False, iso=False):
    """Return abbreviated weekday name for weekday.
    
    This function assumes that ``weekday`` follows the
    ``locale`` module's convention (where Sunday = 1),
    unless one of the keywords is true. If ``dt`` is
    true and ``iso`` is false, the convention used by
    the ``weekday`` method of a ``date`` or ``datetime``
    object is used (so Monday = 0 and Sunday = 6); if
    ``iso`` is true, the ISO convention is assumed
    (Monday = 1 and Sunday = 7). Why there have to be
    three different conventions for this is beyond me.
    """
    weekday = _convert_weekday(weekday, dt, iso)
    return nl_langinfo(
        getattr(locale, 'ABDAY_{}'.format(weekday))
    )


def dt_weekdayname(dt):
    """Return abbreviated weekday name for datetime.
    """
    return dt.strftime("%a")


def weekdayname_long(weekday, dt=False, iso=False):
    """Return long weekday name for weekday.
    
    The parameters are treated the same as for the
    ``weekdayname`` function.
    """
    weekday = _convert_weekday(weekday, dt, iso)
    return nl_langinfo(
        getattr(locale, 'DAY_{}'.format(weekday))
    )


def dt_weekdayname_long(dt):
    """Return long weekday name for datetime.
    """
    return dt.strftime("%A")


def monthname(month):
    """Return abbreviated month name for month.
    """
    return nl_langinfo(
        getattr(locale, 'ABMON_{}'.format(month))
    )


def dt_monthname(dt):
    """Return abbreviated month name for datetime.
    """
    return dt.strftime("%b")


def monthname_long(month):
    """Return long month name for month.
    """
    return nl_langinfo(
        getattr(locale, 'MON_{}'.format(month))
    )


def dt_monthname_long(dt):
    """Return long month name for datetime.
    """
    return dt.strftime("%B")

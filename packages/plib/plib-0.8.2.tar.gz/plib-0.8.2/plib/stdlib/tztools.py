#!/usr/bin/env python
"""
Module TZTOOLS -- PLIB Time Zone Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains useful ``tzinfo`` subclasses,
based on those in the Python documentation for the
``datetime`` module.
"""

import time as _time
from datetime import tzinfo, timedelta


# TZINFO code cribbed from Python docs for datetime module

ZERO = timedelta(0)


class UTCTimezone(tzinfo):
    """Fixed time zone for UTC.
    """
    
    def utcoffset(self, dt):
        return ZERO
    
    def tzname(self, dt):
        return "UTC"
    
    def dst(self, dt):
        return ZERO


STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET


class LocalTimezone(tzinfo):
    """Time zone with DST support for system local time.
    """
    
    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET
    
    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO
    
    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]
    
    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

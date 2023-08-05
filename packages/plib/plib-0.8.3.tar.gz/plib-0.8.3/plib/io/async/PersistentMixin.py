#!/usr/bin/env python
"""
Module PersistentMixin
Sub-Package IO.ASYNC of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the asynchronous PersistentMixin class.
"""

from plib.io.async import AsyncCommunicator
from plib.io.comm import PersistentCommunicator


class PersistentMixin(AsyncCommunicator, PersistentCommunicator):
    pass

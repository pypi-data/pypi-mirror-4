#!/usr/bin/env python
"""
Module _DEFS
Sub-Package STDLIB.CLASSES of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains exception definitions for use
with the ``StateMachine`` class.
"""

class StateMachineException(Exception): pass

class InvalidState(StateMachineException): pass
class InvalidInput(StateMachineException): pass
class RecursiveTransition(StateMachineException): pass

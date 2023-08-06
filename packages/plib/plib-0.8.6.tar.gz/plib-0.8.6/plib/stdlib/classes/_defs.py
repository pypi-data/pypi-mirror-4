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

# These are defined in a separate file so they can be
# imported from the plib.stdlib.classes namespace without
# mucking up the ModuleProxy machinery

class StateMachineException(Exception): pass

class InvalidState(StateMachineException): pass
class InvalidInput(StateMachineException): pass
class RecursiveTransition(StateMachineException): pass

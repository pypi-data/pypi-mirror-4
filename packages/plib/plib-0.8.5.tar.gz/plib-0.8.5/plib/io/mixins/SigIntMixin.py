#!/usr/bin/env python
"""
Module SigIntMixin
Sub-Package IO.MIXINS of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ``SigIntMixin`` class. This is a mixin
class for servers that can be closed by Ctrl-C (or by other
termination signals if the ``term_sigs`` class field is
changed in a subclass), but which do not need any other complex
functionality.
"""

import signal


class SigIntMixin(object):
    """Mixin class for servers to do controlled shutdown on Ctrl-C.
    
    The signals to be trapped and treated as "termination" signals
    can be changed by overriding the ``term_sigs`` class field.
    
    Note that this is not, strictly speaking, new functionality;
    Python by default traps Ctrl-C and raises KeyboardInterrupt,
    which by default causes a program exit; but that does not allow
    for the program to do any shutdown processing unless it
    explicitly traps the exception, which does not always fit in
    with the program's structure. This class traps the signal and
    integrates it into the program's general signal handler. The
    Python default also prints a messy traceback, which this class
    eliminates.
    """
    
    term_sigs = [signal.SIGINT]
    
    terminate_flag = False
    
    def setup_term_sig_handler(self):
        """Set up the termination signal handler.
        
        The ``handler_attr`` class field gives the name of the
        instance method that should be called when a termination
        signal is received. The method must take a single integer
        parameter which will be the received signal number. Note
        that if this field is left at ``None``, no signal handler
        will be installed.
        """
        for sig in self.term_sigs:
            signal.signal(sig, self.term_sig_handler)
    
    def term_sig_handler(self, sig, frame=None):
        """Tell the server to break out of its ``serve_forever`` loop.
        """
        self.terminate_flag = True

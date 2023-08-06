#!/usr/bin/env python
"""
Module PServerBase
Sub-Package IO.CLASSES of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PServerBase class, which can be used as
a mixin for any server that conforms to the API of the I/O server
classes in PLIB.STDLIB. This mixin class adds general signal
handling and logging facilities and redirection of the standard
file descriptors, if required. Note that this class does *not*
do anything special to "daemonize" itself or decouple itself from
its parent environment; all it does is set its root directory to
something sane, and redirect I/O if desired. (On any Unix where
a shell script can background a process with the & parameter,
there doesn't seem to be much point in having each daemon program
do the "double fork" itself, not to mention worrying about process
groups, controlling terminals, etc.--since the shell script is
effectively the first fork, and the backgrounding with & is the
second (and also decouples from the shell's tty), what's left?)
"""

import sys
import os
import datetime
import logging
import signal

from plib.io.mixins import SigIntServerMixin

# We include SIGINT here because it appears to get masked when a script
# is backgrounded, we want to unmask it just in case (we could go back
# to the default Python handler that raises KeyboardInterrupt, but it's
# easier and neater just to trap it ourselves)

sigdata = {
    'SIGABRT': ("aborted", 4),
    'SIGHUP': ("hangup", 1),
    'SIGINT': ("interrupt", 3),
    'SIGQUIT': ("quit", 2),
    'SIGTERM': ("terminated", 0),
    None: ("unknown shutdown", -1) }

for signame in sigdata.iterkeys():
    if signame is not None:
        # Allows for systems where some signals don't exist; those signals
        # will simply be non-functional
        sig = getattr(signal, signame, 0)
        setattr(sys.modules[__name__], signame, sig)


def sigdata_dict(index):
    result = {}
    for key, value in sigdata.iteritems():
        if key is not None:
            sig = getattr(sys.modules[__name__], key)
        else:
            sig = key
        if sig != 0:
            result[sig] = value[index]
    return result


def sigdata_list():
    result = []
    for key in sigdata.iterkeys():
        if key is not None:
            sig = getattr(sys.modules[__name__], key)
            if sig != 0:
                result.append(sig)
    return result


class PServerBase(SigIntServerMixin):
    """Server mixin class providing enhanced common functionality.
    
    Generic base server mixin class, can be used with any type of server
    (sync, async, forking). Implements signal handling for controlled
    termination, and log file functionality. The intent is to trap any
    signal that might be used to indicate general 'program shutdown' as
    opposed to some specific error condition (i.e., any signal where it
    can be assumed that controlled shutdown of the Python interpreter
    is possible).
    """
    
    sig_msgs = sigdata_dict(0)
    ret_codes = sigdata_dict(1)
    term_sigs = sigdata_list()
    sig_methods = {}
    
    terminate_sig = None
    
    if os.name == 'posix':
        log_root = os.path.expanduser("~")
        dir_root = "/"
        log_namestr = ".%(name)s/%(name)s.log"
    else:
        log_root = os.getenv("HOME")
        dir_root = log_root
        log_namestr = "%(name)s.log"
    log_str = "%s %s, time %s"
    server_name = "server"
    
    # This can be set to False for debugging purposes, to allow log entries to
    # be printed to the terminal; if may also be useful if the server is being
    # run by another master process that handles stdin and stdout for it.
    
    redirect_files = True
    
    bind_addr = ("localhost", 9999)
    handler_class = None
    
    def __init__(self, server_addr=None, handler_class=None):
        if server_addr is None:
            server_addr = self.bind_addr
        if handler_class is None:
            handler_class = self.handler_class
        super(PServerBase, self).__init__(server_addr, handler_class)
    
    def server_start(self):
        os.chdir(self.dir_root)
        
        self.logger = self.init_logging()
        
        if self.redirect_files:
            self.log_msg("redirecting standard file descriptors")
            
            if os.name == 'posix':
                # On POSIX systems we can just read/write to /dev/null
                devnull_path = os.path.join("/dev", "null")
                dev_null = open
            else:
                # Hack to emulate a file-like object that does no I/O
                class dev_null(file):
                    def read(self, *args):
                        # Nothing to read
                        return ""
                    readline = read
                    def readlines(self, *args):
                        return []
                    def write(self, *args):
                        # Force this to be a no-op
                        pass
                    writelines = truncate = write
                    def flush(self):
                        # Force this to be a no-op
                        pass
                # We still need a real file so the object has a real fileno
                devnull_path = os.path.join(
                    self.dir_root, "%s_devnull" % self.server_name)
                open(devnull_path, 'w').close()  # creates a 0-byte file
            
            self.dev_null_r = dev_null(devnull_path, 'r')
            self.dev_null_w = dev_null(devnull_path, 'w')
            sys.stdout.flush()
            sys.stderr.flush()
            os.dup2(self.dev_null_r.fileno(), sys.stdin.fileno())
            os.dup2(self.dev_null_w.fileno(), sys.stdout.fileno())
            os.dup2(self.dev_null_w.fileno(), sys.stderr.fileno())
        
        super(PServerBase, self).server_start()
        
        self.log_msg("started")
    
    def init_logging(self):
        log_filename = os.path.join(
            self.log_root, self.log_namestr % {'name': self.server_name})
        logging.basicConfig(filename=log_filename, level=logging.INFO)
        return logging.getLogger()
    
    def log_msg(self, msg, err=False):
        log_entry = self.log_str % (
            self.server_name, msg, datetime.datetime.now())
        getattr(self.logger, ('info', 'error')[err])(log_entry)
        if not self.redirect_files:
            print log_entry
    
    def handle_error(self):
        self.log_msg("exception occurred", err=True)
        from cStringIO import StringIO
        import traceback
        s = StringIO()
        traceback.print_exc(file=s)
        self.log_msg(s.getvalue(), err=True)
        s.close()
    
    def ret_code(self):
        return self.ret_codes[self.terminate_sig]
    
    def term_sig_handler(self, sig, frame=None):
        """Add ability to specify a dispatch method for sig.
        """
        
        # This sets the terminate flag
        super(PServerBase, self).term_sig_handler(sig, frame)
        
        # Store the signal for logging on shutdown
        self.terminate_sig = sig
        
        # Dispatch to method if present
        if sig in self.sig_methods:
            fn = getattr(self, self.sig_methods[sig])
            fn(sig, frame)
    
    def server_close(self):
        super(PServerBase, self).server_close()
        
        self.log_msg(self.sig_msgs[self.terminate_sig])
        
        if self.redirect_files:
            self.dev_null_w.close()
            self.dev_null_r.close()
            if os.name != 'posix':
                # Undo the /dev/null stdin emulation hack
                devnull_path = os.path.join(
                    self.dir_root, "%s_devnull" % self.server_name)
                os.remove(devnull_path)
        
        logging.shutdown()

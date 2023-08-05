#!/usr/bin/env python
"""
Module SERVERPROXY -- Server Proxy Object
Sub-Package STDLIB.COMM of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

This module contains the ``ServerProxy`` class, which is used
by the ``fork_server`` function in this sub-package to create
child processes that run servers. This class is separated into
its own module so that the child process that uses it does not
need to import the ``forkserver`` module or its dependencies
(this really only makes a difference on Windows, where the
``multiprocessing`` module is used to run the child process).
"""


class ServerProxy(object):
    
    def __init__(self, server_class, server_addr=None, handler_class=None):
        self.server_class = server_class
        self.server_addr = server_addr
        self.handler_class = handler_class
    
    def start_server(self):
        # Allow a tuple of (<module_name>, <class_name>) for the server
        # and handler classes so they can be imported only in the child
        # process, to reduce the memory footprint prior to forking
        for attrname in ('server_class', 'handler_class'):
            obj = getattr(self, attrname)
            if isinstance(obj, tuple):
                from plib.stdlib.imp import import_from_module
                setattr(self, attrname, import_from_module(*obj))
        if self.handler_class is not None:
            self.server = self.server_class(
                self.server_addr, self.handler_class)
        elif self.server_addr is not None:
            self.server = self.server_class(
                self.server_addr)
        else:
            self.server = self.server_class()
    
    def run_server(self):
        self.server.serve_forever()


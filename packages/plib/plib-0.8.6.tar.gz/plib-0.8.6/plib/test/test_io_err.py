#!/usr/bin/env python
"""
TEST_IO_ERR.PY -- test script for sub-package STDLIB of package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests checking the handling of various
errors or unusual conditions in the I/O modules in the
PLIB.STDLIB sub-package.
"""

import signal
import unittest

# Only run these tests when SIGCHLD is available

if hasattr(signal, 'SIGCHLD'):
    
    import os
    from errno import ECHILD
    
    # For use in hack to get exception info in server exit code below
    import exceptions
    
    from plib.io.mixins import SigChldServerMixin, SigIntServerMixin
    
    from io_testlib import IOChannelTest
    from io_testlib_blocking import BlockingHandler, ForkingServer
    from io_testlib_blocking import SocketClient as BlockingClient
    
    
    class EarlyShutdownClient(BlockingClient):
        # Simple client just records received data
        
        keep_alive = True  # so the channel will stay open after data is read
        
        def process_data(self):
            self.result = self.read_data
    
    
    class EarlyShutdownHandler(BlockingHandler):
        pass  # keep_alive is true by default for server-side communicators
    
    
    # Hack to get exception info on server shutdown
    
    exception_names = dir(exceptions)
    
    def exception_number(e):
        return exception_names.index(e.__class__.__name__) + 130
    
    
    class EarlyShutdownServer(SigChldServerMixin, SigIntServerMixin,
            ForkingServer):
        # Traps SIGTERM, so we can trigger a shutdown while children are
        # active and confirm that the server shuts them down gracefully
        
        term_sigs = [signal.SIGTERM]
        
        child_was_open = False
        
        def server_close(self):
            # Confirm that a child is still open
            self.child_was_open = bool(self.active_children)
            super(EarlyShutdownServer, self).server_close()
        
        def serve_forever(self):
            # Wrap the super call just in case an error happens in here,
            # so we don't mistake it for an error in the child code below
            try:
                super(EarlyShutdownServer, self).serve_forever()
            except Exception, e:
                # Hack to get some info on which exception it was (see
                # note below on range of exit codes used)
                os._exit(exception_number(e))
            
            # We signal our unique errors with codes that are higher than
            # any possible errno value, but lower than the range PLIB uses
            # for forking errors, so we can tell which error we got
            if not self.child_was_open:
                # The child shut down early
                os._exit(198)
            if self.active_children:
                # The shutdown process didn't clear active_children
                os._exit(197)
            # If we get to here, there was a child and it's no longer in
            # active_children, so we should be home free, but we're
            # paranoid so we check further
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)  # should raise OSError
            except OSError, e:
                os._exit(e.errno)  # hopefully this equals ECHILD!
            # If we get here, there were children, bad!
            if pid:
                if os.WIFSIGNALED(status):
                    os._exit(-os.WTERMSIG(status))
                elif os.WIFEXITED(status):
                    os._exit(os.WEXITSTATUS(status))
            # Just in case something went awry above
            os._exit(199)
    
    
    class BlockingEarlyShutdownTest(IOChannelTest, unittest.TestCase):
        
        client_class = EarlyShutdownClient
        handler_class = EarlyShutdownHandler
        server_class = EarlyShutdownServer
        
        test_data = "Python rocks!"
        
        def test_shutdown(self):
            client = self.client_class()
            # This will do one round-trip exchange but keep the channel open
            client.client_communicate(self.test_data, ('localhost', self.server_port))
            self.assert_(not client.closed)
            self.assertEqual(client.result, self.test_data)
            # Now shut down the server while the handler is still active
            self.server.stop()
            exitcode = self.server.exitcode()
            self.server = None
            self.assertEqual(exitcode, ECHILD)


if __name__ == '__main__':
    if not hasattr(signal, 'SIGCHLD'):
        print "SIGCHLD not available, skipping related tests."
    unittest.main()

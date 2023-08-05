#!/usr/bin/env python
"""
Module PROCESSWRAPPER -- Child Process Wrapper Object
Sub-Package STDLIB.COMM of Package PLIB -- General Python Utilities
Copyright (C) 2008-2012 by Peter A. Donis

This module contains the ``ProcessWrapper`` class, which provides
a portable interface to child processes and their exit status.
This class is used by the specialized forking functions in this
library, and by the ``SigChldMixin`` class in ``plib.stdlib``.

Note that on Windows the ``multiprocessing`` module is used. (We
purposely do *not* use that module on Unix-type systems, because
it is too heavyweight for what we need here, not to mention that
it doesn't do proper SIGCHLD handling on Unix-type systems--it
doesn't ignore SIGCHLD, as PLIB does by default, so that the
kernel will reap zombies when they arise, but it also does not
trap SIGCHLD and reap zombies itself--instead they are left
hanging around until the parent exits. If there were a lighter
Windows alternative we would use it, but there isn't.)
"""

from ._childwrapper import ChildWrapper

try:
    # Use this to determine what mechanism we'll use to create
    # child processes: either the Unix fork ...
    from os import fork
    OS_FORK = True
    del fork

except (ImportError, AttributeError):
    # ... or the Windows Rube Goldberg contraption :-)
    OS_FORK = False

if OS_FORK:
    # We have fork (whew!), so do it the right way :-)
    
    import os
    import signal
    
    
    class ProcessWrapper(ChildWrapper):
        # TODO: any way to enforce shutdown_with_parent here?
        
        pid = None
        term_sig = signal.SIGTERM
        
        def start(self):
            if self.pid is None:
                pid = os.fork()
                if pid == 0:
                    # Child process
                    e = self._target(*self._args, **self._kwargs)
                    if not isinstance(e, int):
                        e = 0
                    os._exit(e)
                # Parent process
                self.pid = pid
            else:
                raise RuntimeError("Process already started.")
        
        def stop(self):
            if self.pid is not None:
                os.kill(self.pid, self.term_sig)
        
        def _check_exited(self, wait):
            # Internal method to check exit status
            if self.pid is not None:
                try:
                    pid, status = os.waitpid(self.pid, (os.WNOHANG, 0)[wait])
                except os.error:
                    pid = None
                if pid == self.pid:
                    if os.WIFSIGNALED(status):
                        self._exitcode = -os.WTERMSIG(status)
                    elif os.WIFEXITED(status):
                        self._exitcode = os.WEXITSTATUS(status)
                    else:
                        raise RuntimeError("Invalid process exit status: %r" %
                            status)
                    self.pid = None
        
        def check(self):
            self._check_exited(0)
            return self.pid is None
        
        def wait(self):
            self._check_exited(1)


else:
    # No fork on Windows, have to use the multiprocessing module
    # with some extra gymnastics of our own
    
    from multiprocessing import process
    
    
    class ChildProcess(process.Process):
        
        def _bootstrap(self):
            import sys
            import os
            import itertools
            from multiprocessing import util
            
            try:
                self._children = set()
                self._counter = itertools.count(1)
                try:
                    os.close(sys.stdin.fileno())
                except (OSError, ValueError):
                    pass
                process._current_process = self  # ugly!
                util._finalizer_registry.clear()
                util._run_after_forkers()
                util.info('child process calling self.run()')
                try:
                    # All this just so we can let the run method
                    # return an actual exit code; WTF isn't this
                    # already in there? !@#$%^&*
                    exitcode = self.run()
                    if exitcode is None:
                        exitcode = 0
                finally:
                    util._exit_function()
            except SystemExit, e:
                if not e.args:
                    exitcode = 1
                elif type(e.args[0]) is int:
                    exitcode = e.args[0]
                else:
                    sys.stderr.write(e.args[0] + '\n')
                    sys.stderr.flush()
                    exitcode = 1
            except:
                exitcode = 1
                import traceback
                sys.stderr.write('Process %s:\n' % self.name)
                sys.stderr.flush()
                traceback.print_exc()
            
            util.info('process exiting with exitcode %d' % exitcode)
            return exitcode
        
        def run(self):
            # And now we need to actually return the exit code
            # (at least this part is easily implemented...)
            if self._target:
                return self._target(*self._args, **self._kwargs)
    
    
    class ProcessWrapper(ChildWrapper):
        
        process = None
        
        def start(self):
            if self.process is None:
                self.process = ChildProcess(
                    target=self._target, args=self._args, kwargs=self._kwargs)
                self.process.daemon = self.shutdown_with_parent
                self.process.start()
            else:
                raise RuntimeError("Process already started.")
        
        def stop(self):
            self.process.terminate()
        
        def check(self):
            if self.process is None:
                return True
            if not self.process.is_alive():
                self._exitcode = self.process.exitcode
                self.process = None
                return True
            return False
        
        def wait(self):
            self.process.join()
            self._exitcode = self.process.exitcode
            self.process = None

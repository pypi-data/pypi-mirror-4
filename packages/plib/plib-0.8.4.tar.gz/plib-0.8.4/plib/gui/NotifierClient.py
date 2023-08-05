#!/usr/bin/env python
"""
Module NotifierClient
Sub-Package GUI of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the NotifierClient class. This is
a mixin class designed to allow an async socket I/O class
to multiplex its event loop with a GUI event loop. Due to
limitations in some GUI toolkits, this functionality is
implemented in two different ways, depending on the toolkit
in use:

- For Qt 3/4 and KDE 3/4, the PSocketNotifier class is present,
  and its functionality is used to allow the GUI event loop to
  respond to socket events. This is the desired approach.

- For GTK and wxWidgets, there is no straightforward way to
  make the GUI event loop "see" socket events; there are possible
  approaches involving threading, but these are complex and prone
  to brittleness. Instead, the kludgy but workable approach is
  taken of making the asnyc socket I/O ``select`` loop the "primary"
  one, and using the GUI application's ``process_events`` method
  to pump its events based on a ``select`` timeout.
"""

from plib.gui import main as gui

app_obj = None

if hasattr(gui, 'PSocketNotifier'): # Qt 3/4 and KDE 3/4
    
    import asyncore
    
    from plib.gui.defs import *
    
    notify_methods = {
        NOTIFY_READ: ('readable', 'read'),
        NOTIFY_WRITE: ('writable', 'write') }
    
    
    class NotifierClient(object):
        """Mixin class to multiplex async socket client with GUI event loop.
        
        This class is intended to be mixed in with an async socket client
        class; for example::
            
            class MyClient(NotifierClient, async.SocketClient):
                pass
        
        For most purposes this class functions as a "drop-in" mixin; no
        method overrides or other customization should be necessary (other
        than the obvious override of ``process_data`` to do something with
        data received from the socket).
        
        Note that the notifier client object must be instantiated
        *before* the application's event loop is started, or no
        socket events will be processed. (Possible places to do that are
        constructors for any client widget classes, or the app itself
        if you are defining your own app class; or in any methods that
        are called from those constructors, such as the ``_create_panels``
        method of a main panel.)
        
        Note also that we override the ``do_loop`` method to yield control
        back to the GUI event loop, and the ``check_done`` method to
        un-yield so the function that called ``do_loop`` (normally the
        ``client_communicate`` method) can return as it normally would.
        This allows user code to be written portably, so that it does not
        even need to know which event loop is actually running.
        """
        
        notifier_class = gui.PSocketNotifier
        notifiers = None
        done_callback = None
        yielded = False
        
        def get_notifier(self, notify_type):
            sfn, nfn = notify_methods[notify_type]
            result = self.notifier_class(self, notify_type,
                getattr(self, sfn), getattr(asyncore, nfn))
            result.auto_enable = False # we'll do the re-enable ourselves
            return result
        
        def check_notifiers(self):
            if self.notifiers:
                for notifier in self.notifiers:
                    notifier.set_enabled(notifier.select_fn())
        
        def do_connect(self, addr):
            super(NotifierClient, self).do_connect(addr)
            if self.connected or self.connect_pending:
                self.notifiers = [self.get_notifier(t)
                    for t in (NOTIFY_READ, NOTIFY_WRITE)]
                self.check_notifiers()
        
        def start(self, data):
            super(NotifierClient, self).start(data)
            self.check_notifiers()
        
        # FIXME: Currently we use an ugly hack for Qt/KDE 3 to
        # allow do_loop to be called transparently by a
        # NotifierClient, even though the async I/O loop is not
        # in use. For Qt/KDE 4 there is a documented method for
        # yielding back to the GUI event loop, and un-yielding
        # when necessary; this method is implemented in the
        # enter_yield and exit_yield methods of the application
        # object. For Qt/KDE 3, however, the method used is
        # what is done below if the enter_yield and exit_yield
        # methods are not present on the application object;
        # the documentation says about these method calls, "only
        # do this if you really know what you are doing". This
        # is not very comforting. :-) However, the only other
        # method, calling the async loop with the process_events
        # method of the app object as a callback (as is done for
        # Gtk/wxWidgets below), does not perform well with Qt/KDE,
        # particularly when it is done as a "local" event loop
        # inside a handler for the underlying GUI loop. So we
        # are basically stuck with the ugly hack below. No
        # guarantees are made that this will work reliably; you
        # have been warned. :-) That said, it appears to work on
        # the Linux Qt/KDE implementations I have access to. Given
        # that and the fact that Qt 3 is now being obsoleted, I
        # don't intend to expend much more effort on this issue.
        
        def _doyield(self):
            # Start a local instance of the GUI event loop
            # (NOTE: *not* to be called from user code!)
            self.yielded = True
            if hasattr(app_obj, 'enter_yield'):
                app_obj.enter_yield()
            else:
                # XXX Why does this hack only work if the
                # enterLoop call is made directly from here,
                # instead of wrapping it up in the enter_yield
                # method of the app object?
                app_obj.eventLoop().enterLoop()
        
        def do_loop(self, callback=None):
            """Override to yield back to the GUI event loop.
            """
            self.done_callback = callback
            if not self.yielded:
                self._doyield()
        
        def handle_write(self):
            super(NotifierClient, self).handle_write()
            self.check_notifiers()
        
        def handle_read(self):
            super(NotifierClient, self).handle_read()
            self.check_notifiers()
        
        def _unyield(self):
            # Return from a local instance of the GUI event loop
            # (NOTE: *not* to be called from user code!)
            self.done_callback = None
            self.yielded = False
            if hasattr(app_obj, 'exit_yield'):
                app_obj.exit_yield()
            else:
                # XXX Why does this hack only work if the
                # exitLoop call is made directly from here,
                # instead of wrapping it up in the exit_yield
                # method of the app object?
                app_obj.eventLoop().exitLoop()
        
        def check_done(self):
            """Override to un-yield from the GUI event loop if done.
            """
            super(NotifierClient, self).check_done()
            if self.yielded and (((self.done_callback is not None) and
                                  (self.done_callback() is False)) or
                                 self.done):
                self._unyield()
        
        def close(self):
            """Override to ensure we un-yield when closed.
            """
            super(NotifierClient, self).close()
            if self.yielded:
                self._unyield()
        
        def handle_close(self):
            if self.notifiers:
                del self.notifiers[:]
            super(NotifierClient, self).handle_close()
    
    
    class NotifierApplication(gui.PApplication):
        
        def createMainWidget(self):
            global app_obj
            app_obj = self
            return super(NotifierApplication, self).createMainWidget()


else: # GTK and wxWidgets
    
    
    class NotifierClient(object):
        """Mixin class to multiplex async socket client with GUI event loop.
        
        This class is intended to be mixed in with an async socket client
        class; for example::
            
            class MyClient(NotifierClient, async.SocketClient):
                pass
        
        For most purposes this class functions as a "drop-in" mixin; no
        method overrides or other customization should be necessary (other
        than the obvious override of ``process_data`` to do something with
        data received from the socket).
        
        Note that the notifier client object must be instantiated
        *before* the application's event loop is started, or no
        socket events will be processed. (Possible places to do that are
        constructors for any client widget classes, or the app itself
        if you are defining your own app class; or in any methods that
        are called from those constructors, such as the ``_create_panels``
        method of a main panel.)
        """
        
        poll_timeout = 0.1  # needs to be a short timeout to keep GUI snappy
        
        def do_connect(self, addr):
            super(NotifierClient, self).do_connect(addr)
            if self.connected or self.connect_pending:
                app_obj.notifier_client = self
        
        def handle_close(self):
            app_obj.notifier_client = None
            super(NotifierClient, self).handle_close()
    
    
    class NotifierApplication(gui.PApplication):
        
        notifier_client = None
        
        def createMainWidget(self):
            global app_obj
            app_obj = self
            return super(NotifierApplication, self).createMainWidget()
        
        def _eventloop(self):
            """Use the async I/O loop with a timeout to process GUI events.
            """
            if self.notifier_client is not None:
                self.process_events() # start with a clean slate
                self.notifier_client.do_loop(self.process_events)
                self.process_events() # clear all events before exiting
            else:
                super(NotifierApplication, self)._eventloop()


gui.default_appclass[0] = NotifierApplication

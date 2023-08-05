#!/usr/bin/env python
"""
Module APP -- GUI Application Classes
Sub-Package GUI.BASE of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the classes that form the basic GUI application framework.
"""

import sys
import os.path

from plib.stdlib.ini import PIniFile
from plib.stdlib.ini.defs import *

from plib.gui.defs import *


class PBaseWindowBase(object):
    """Base class for "window" widgets.
    
    This class is mainly for inheritance purposes; it implements
    the basic window behaviors, but does not have all the extra
    stuff in ``PTopWindow`` that relates specifically to being an
    application's main window.
    """
    
    clientwidgetclass = None
    
    defaultcaption = "Window"
    placement = (SIZE_NONE, MOVE_NONE)
    sizeoffset = 160
    
    _clientattrs = ('defaultcaption', 'placement', 'sizeoffset')
    
    def __init__(self, parent, cls):
        self.shown = False
        
        # Figure out if parent is another window or the application
        # (normally only a PTopWindow will have the application as
        # its parent directly, but we implement the check here
        # because it's easier)
        if hasattr(parent, 'app'):
            self.app = parent.app
            self._parent = parent
        elif isinstance(parent, PApplicationBase):
            self.app = parent
            self._parent = None
        else:
            # This shouldn't happen, but just in case...
            self.app = None
            self._parent = None
        
        self.set_caption(self.defaultcaption)
        
        self._set_client_class(cls)
        
        self.clientwidget = self.createclient()
    
    def set_caption(self, caption):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_client_class(self, cls):
        if cls is not None:
            self.clientwidgetclass = cls
        if self.clientwidgetclass is not None:
            cls = self.clientwidgetclass
            for attrname in self._clientattrs:
                if hasattr(cls, attrname):
                    setattr(self, attrname, getattr(cls, attrname))
                elif not hasattr(self, attrname):
                    setattr(self, attrname, None)
    
    def createclient(self):
        """Create the client widget if its class is given.
        """
        
        if self.clientwidgetclass is not None:
            return self.clientwidgetclass(self)
        return None
    
    def get_clientsize(self):
        """Return tuple of (width, height) needed to wrap client.
        """
        c = self.clientwidget
        return (c.preferred_width(), c.preferred_height())
    
    def sizetoscreen(self, maximized=False):
        """Size the window to the screen.
        
        Size the window to be sizeoffset pixels from each screen edge,
        or maximized if the parameter is True.
        """
        raise NotImplementedError
    
    def sizetoclient(self, clientwidth, clientheight):
        """Size the window to a client widget.
        
        Size the window to fit the given client width and height.
        """
        raise NotImplementedError
    
    def center(self):
        """Center the window in the primary screen.
        """
        raise NotImplementedError
    
    def init_placement(self):
        size, pos = self.placement
        if size == SIZE_CLIENTWRAP:
            self.sizetoclient(*self.get_clientsize())
        elif size in (SIZE_MAXIMIZED, SIZE_OFFSET):
            self.sizetoscreen(size == SIZE_MAXIMIZED)
        if (pos == MOVE_CENTER) and (size != SIZE_MAXIMIZED):
            self.center()
    
    def show_init(self):
        """Should always call from derived classes to ensure proper setup.
        """
        if not self.shown:
            # Do placement just before showing for first time
            self.init_placement()
            self.shown = True
    
    def clientcanclose(self):
        return (not hasattr(self.clientwidget, 'acceptclose')) \
            or self.clientwidget.acceptclose()
    
    def acceptclose(self):
        """Return False if window should not close based on current state.
        """
        return self.clientcanclose()
    
    def _canclose(self):
        # Internal method, should not be overridden (override acceptclose
        # to add/modify external behavior)
        return self.acceptclose()
    
    def exit(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PAboutDialogBase(object):
    """Base class for about dialogs.
    
    Implements mapping of standard fields in about data to methods
    of about dialog that will process the data, by hacking
    ``__getattribute__`` to substitute attribute names on the fly.
    """
    
    attrmap = {}
    
    def __init__(self, parent):
        self.mainwidget = parent
    
    def __getattribute__(self, name):
        # Monkeypatch attribute name if necessary
        attrmap = super(PAboutDialogBase, self).__getattribute__('attrmap')
        if name in attrmap:
            name = attrmap[name]
        return super(PAboutDialogBase, self).__getattribute__(name)


def _munge_prefsdata(prefsdata):
    # For re-ordering prefs data if the more readable
    # ordering was used (see PTopWindowBase constructor below)
    return (prefsdata[0], prefsdata[2], prefsdata[1])


def _get_settings(prefsdata):
    # Only call after ordering has been munged if needed (as above)
    from plib import ini
    prefsname, specs, _ = prefsdata
    inispecs = [(sname, [(oname, otype, default)
        for oname, otype, default, __ in opts])
            for sname, _, opts in specs]
    return PIniFile(prefsname, inispecs)


def _fix_prefsdata(settings, prefsdata):
    # Only call after _get_settings (as above)
    _, specs, style = prefsdata
    dlgspecs = []
    for sname, title, opts in specs:
        dlgspecs.append((sname, title))
        dlgspecs.extend(("%s_%s" % (sname, oname), label)
            for oname, _, __, label in opts)
    return settings, dict(dlgspecs), style


window_optnames = ("left", "top", "width", "height")


class PTopWindowBase(PBaseWindowBase):
    """Base class for 'top window' widgets.
    
    A top window is a 'plain' main application window; it has no
    frills like menus, toolbars, status bars, etc. built in (if
    you want those frills, use PMainWindow instead). It does have
    some basic functionality, however, using the following class
    fields:
    
    aboutdialogclass -- gives class to be used to display the 'about' dialog
    box. This class is normally set internally to PLIB and should not need
    to be overridden by the user.
    
    clientwidgetclass -- gives the class of the client widget (actually can
    be any callable with the right signature that returns a widget); if None,
    no client widget is created automatically (widgets can still be created
    manually in user code). The callable must take one argument, which will
    be the PTopWindow instance creating it.
    
    Note that all the rest of the options below can be read from a client
    widget class, so the need to set them by subclassing PTopWindow directly
    should be rare:
    
    aboutdata -- gives data for display in the 'about' dialog.
    
    prefsdata -- gives parameters for constructing the 'preferences' dialog.
    
    defaultcaption -- gives the caption if no editor object is found
    
    placement -- how the window should be sized (normal, maximized, wrapped to
    the client widget, or offset from the screen edge) and positioned on the
    screen (centered, or left to the system's default positioning)
    
    sizeoffset -- how many pixels from the edge of the screen this window
    should be sized (only used if placement indicates sizing to offset from
    screen edge)
    """
    
    aboutdialogclass = None
    abouttoolkitfunc = None
    
    aboutdata = {}
    prefsdata = None
    
    defaultcaption = "Top Window"
    
    _clientattrs = ('aboutdata', 'prefsdata') + PBaseWindowBase._clientattrs
    
    def __init__(self, parent, cls=None):
        PBaseWindowBase.__init__(self, parent, cls)
        
        self._setup_aboutdata()
        self._setup_prefsdata()
        
        self.prefsdialog = self.createprefsdialog()
    
    def get_basename(self):
        """Return the base name of the application script.
        """
        return os.path.splitext(os.path.basename(sys.argv[0]))[0]
    
    def _setup_aboutdata(self):
        if 'icon' in self.aboutdata:
            self.set_iconfile(self.aboutdata['icon'])
    
    def _setup_prefsdata(self):
        size, pos = self.placement
        if self.prefsdata:
            # Support alternate ordering of prefs parameters
            if isinstance(self.prefsdata[1], int):
                # Re-order to put the section type flag after the
                # list of labels (having the list last is more
                # readable in the class definition, but the actual
                # dialog constructor wants the flag last)
                self.prefsdata = _munge_prefsdata(self.prefsdata)
            prefsdata = self.prefsdata
        elif (size == SIZE_SETTINGS) or (pos == MOVE_SETTINGS):
            # Create an empty prefsdata object so we can add the
            # settings for window coordinates below
            prefsdata = (
                self.get_basename(), [], SECTION_GROUPBOX)
        else:
            prefsdata = None
        if prefsdata:
            # Add the window placement settings if the class fields
            # for placement are set appropriately
            if (size == SIZE_SETTINGS) or (pos == MOVE_SETTINGS):
                prefsdata[1].append(("window", "Window Placement",
                    [(optname, INI_INTEGER, -1, optname.capitalize())
                        for optname in window_optnames]))
            # Now split out settings from prefsdata if a settings
            # name is given instead of a PIniFile instance
            if isinstance(prefsdata[0], basestring):
                self.settings = _get_settings(prefsdata)
                if self.prefsdata:
                    self.prefsdata = _fix_prefsdata(self.settings, prefsdata)
            else:
                self.settings = prefsdata[0]
        else:
            self.settings = None
    
    def set_iconfile(self, iconfile):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def createprefsdialog(self):
        """Create the preferences dialog if data is given.
        """
        
        if self.prefsdata:
            # This avoids circular imports when this module is first loaded
            from plib.gui import main as gui
            return gui.PPrefsDialog(self, *self.prefsdata)
        return None
    
    def _size_to_settings(self, width, height):
        """Size the window to the given width and height (including frame).
        """
        raise NotImplementedError
    
    def _move_to_settings(self, left, top):
        """Move the window to the given position (including frame).
        """
        raise NotImplementedError
    
    def _get_current_geometry(self):
        """Return the window's current geometry (including frame).
        """
        raise NotImplementedError
    
    def set_settings_placement(self, setsize, setpos):
        # Set previous window placement from settings
        if setsize or setpos:
            left, top, width, height = tuple(
                getattr(self.settings, "window_%s" % optname)
                    for optname in window_optnames)
            if setsize:
                self._size_to_settings(width, height)
            if setpos:
                self._move_to_settings(left, top)
    
    def get_settings_placement(self, setsize, setpos):
        # Store current window size and position in settings
        if setsize or setpos:
            left, top, width, height = self._get_current_geometry()
            for optname in window_optnames:
                setattr(self.settings, "window_%s" % optname,
                    locals()[optname])
    
    def get_coordinates(self):
        """Update settings with current coordinates.
        
        Called by PPrefsDialog before showing the dialog.
        """
        size, pos = self.placement
        self.get_settings_placement(
            size == SIZE_SETTINGS, pos == MOVE_SETTINGS)
    
    def set_coordinates(self):
        """Size/move window to coordinates in settings.
        
        Called by PPrefsDialog when Apply or OK is pressed.
        """
        size, pos = self.placement
        self.set_settings_placement(
            size == SIZE_SETTINGS, pos == MOVE_SETTINGS)
    
    def init_placement(self):
        PBaseWindowBase.init_placement(self)
        self.set_coordinates()
    
    def choose_directory(self, curdir):
        """Display select folder dialog and return chosen folder.
        """
        raise NotImplementedError
    
    def preferences(self):
        if self.prefsdialog:
            self.prefsdialog.showdialog()
    
    def about(self):
        if (self.aboutdata is not None) and \
                (self.aboutdialogclass is not None):
            
            dialog = self.aboutdialogclass(self)
            for key, item in self.aboutdata.iteritems():
                getattr(dialog, key)(item)
            dialog.display()
    
    def about_toolkit(self):
        if self.abouttoolkitfunc is not None:
            self.abouttoolkitfunc()
    
    def _canclose(self):
        result = PBaseWindowBase._canclose(self)
        if result and self.settings:
            self.get_coordinates()
            self.settings.writeini()
        return result


class PApplicationBase(object):
    """Base class for GUI application.
    
    Automatically sizes the main widget and centers it in
    the primary screen if the widget's class flags are set
    appropriately (see PTopWindow).
    
    Descendant app classes should set the class variable
    ``mainwidgetclass`` to the appropriate class object. If this
    is the only customization you want to do, however, you do
    not need to subclass this class--just pass your main window
    class derived from ``PTopWindow`` to the ``runapp`` function;
    see that function's docstring. In fact, you can even pass a
    client widget class to ``runapp``, and it will automatically
    be wrapped in a ``PTopWindow``--or, if you set the keyword
    argument ``use_mainwindow`` to ``True``, a ``PMainWindow``.
    See the ``pyidserver-gui`` and ``scrips-edit`` example
    programs for typical usage.
    
    The only time you should need to subclass this class is to
    override ``createMainWidget`` (to alter the parameters passed
    to the main widget, or do other processing after it's created
    but before the rest of ``__init__``) or to provide other
    functionality that has to be at the application level rather
    than in the main widget (but this should be extremely rare).
    """
    
    mainwidgetclass = None
    
    def __init__(self, arglist=[], cls=None, use_mainwindow=False):
        self.arglist = arglist
        self.mainwin = None
        
        # Set up main widget class
        if self.mainwidgetclass is None:
            # Import here to avoid circular imports; note that we
            # should normally get here only if the ``cls`` parameter
            # is not None (so we have a real client class)
            from plib.gui import main as gui
            if use_mainwindow:
                self.mainwidgetclass = gui.PMainWindow
            else:
                self.mainwidgetclass = gui.PTopWindow
        
        # Set up main application class
        if cls is not None:
            # The ``cls`` parameter should be either a valid main widget
            # class (which will create its own client widget), or a valid
            # client widget class (which will be wrapped in the default
            # main widget)
            self.mainwinclass = cls
        else:
            self.mainwinclass = self.mainwidgetclass
    
    def createMainWidget(self):
        """Create the main widget and return it.
        """
        if issubclass(self.mainwinclass, PTopWindowBase):
            return self.mainwinclass(self)
        return self.mainwidgetclass(self, self.mainwinclass)
    
    def _eventloop(self):
        """Placeholder for derived classes for main event loop.
        """
        raise NotImplementedError
    
    def run(self):
        """Show the main widget and run the main event loop.
        """
        
        self.mainwin.show_init()
        self._eventloop()
    
    def process_events(self):
        """Placeholder for derived classes to pump events outside main loop.
        """
        raise NotImplementedError
    
    def before_quit(self):
        """Placeholder for derived classes to do destructor-type processing.
        """
        pass

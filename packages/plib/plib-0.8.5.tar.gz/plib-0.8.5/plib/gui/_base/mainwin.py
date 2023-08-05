#!/usr/bin/env python
"""
Module MAINWIN -- GUI Main Window Classes
Sub-Package GUI.BASE of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the classes for fully functional decorated GUI main
windows.
"""

from plib.stdlib.builtins import inverted
from plib.stdlib.classtools import Singleton

from plib.gui.defs import *
from plib.gui.common import *
from plib.gui._edit import PEditor

from plib.gui._base import app


class _PDialogBase(Singleton):
    
    def _init(self, parent):
        self._parent = parent


class PMessageBoxMeta(type):
    """Metaclass to automatically set up message box classes.
    """
    
    def __init__(cls, name, bases, dict):
        # Add None to question map and set up answer map
        type.__init__(cls, name, bases, dict)
        questionmap = getattr(cls, 'questionmap')
        questionmap.update({answerNone: None})
        setattr(cls, 'questionmap', questionmap)
        answermap = inverted(questionmap)
        setattr(cls, 'answermap', answermap)


class PMessageBoxBase(_PDialogBase):
    
    __metaclass__ = PMessageBoxMeta
    
    questionmap = {}
    
    def _messagebox(self, type, caption, text,
            button1, button2=None, button3=None):
        """Placeholder for derived classes to implement.
        """
        return None
    
    def _translate(self, type, caption, text,
            button1, button2=answerNone, button3=answerNone):
        
        return self.answermap[self._messagebox(type, caption, text,
            self.questionmap[button1],
            self.questionmap[button2],
            self.questionmap[button3])]
    
    def info(self, caption, text):
        """Information message box.
        """
        return self._translate(MBOX_INFO, caption, text,
            answerOK)
    
    def warn(self, caption, text):
        """Warning message box.
        """
        return self._translate(MBOX_WARN, caption, text,
            answerOK)
    
    def error(self, caption, text):
        """Error message box.
        """
        return self._translate(MBOX_ERROR, caption, text,
            answerOK)
    
    def query2(self, caption, text):
        """OK/Cancel message box.
        """
        return self._translate(MBOX_QUERY, caption, text,
            answerOK, answerCancel)
    
    def query3(self, caption, text):
        """Yes/No/Cancel message box.
        """
        return self._translate(MBOX_QUERY, caption, text,
            answerYes, answerNo, answerCancel)


class PFileDialogBase(_PDialogBase):
    
    def openfiledialog(self, path, filter):
        """Placeholder for derived classes to implement.
        """
        return ""
    
    def savefiledialog(self, path, filter):
        """Placeholder for derived classes to implement.
        """
        return ""


class PMainWindowBase(app.PTopWindowBase):
    """Base class for 'main window' widgets.
    
    The main window is a fancier version of the top window, which
    includes all the frills that PTopWindow leaves out.
    
    If there are any action flags defined, the main window generates a
    menu bar and tool bar and populates them appropriately for the
    actions that are defined. The main window then manages the enable
    state of menu items and buttons based on internal flags and file state.
    
    The main window generates a status bar and populates it with a text
    label widget that can be used to display messages. If other status
    widgets are defined, it adds them to the right side of the status bar.
    
    If the window is the main widget of the application (see PApplication),
    it will be sized and/or centered in the main screen if the class
    variables sized and centered are set to True. (The default is to
    center but not size.)
    
    The key class fields (in addition to those of PTopWindow) and their
    functions are:
    
    editorclass -- gives the class of the editor (actually can be any callable
    with the right signature returning a PEditor or derived class instance);
    if None, the editor is self if self is a mixin of PEditor and a widget;
    if editorclass == clientwidgetclass, the editor is the client widget
    (which must then be a mixin of PEditor and a widget). The PEditor
    constructor takes care of all of these options if used as described in
    its docstring.
    
    menuclass -- gives the class of the menu
    
    toolbarclass -- gives the class of the toolbar
    
    statusbarclass -- gives the class of the status bar
    
    messageboxclass -- gives the class to be used for message dialogs
    
    filedialogclass -- gives the class to be used for file open/save dialogs
    
    Note that the rest of these parameters can be read from a client widget
    class if they exist (see PTopWindow's docstring for more info):
    
    actionflags -- determines the actions that will be created
    
    large_icons -- whether the toolbar icons should be large size
    
    show_labels -- whether toolbar buttons should show labels as well as icons
    (if this is false labels will still be displayed in tooltips)
    
    queryonexit -- whether the window should query the user to confirm before
    closing if it's the main widget of the app
    
    statuswidgets -- determines the widgets that will be added to the status
    bar (see the PStatusBarBase docstring--but note that if a PAutoStatusBar
    is used, this field should be left blank and the widgetspecs field should
    be used (it can be defined either in this class or the status bar class).
    """
    
    editorclass = None
    menuclass = None
    toolbarclass = None
    statusbarclass = None
    actionclass = None
    messageboxclass = None
    filedialogclass = None
    
    actionflags = []
    large_icons = False
    show_labels = False
    queryonexit = True
    statuswidgets = None
    widgetspecs = None
    
    editlist = [ACTION_EDIT]
    pendinglist = [ACTION_APPLY, ACTION_COMMIT, ACTION_OK, ACTION_CANCEL]
    modifiedlist = [ACTION_FILESAVE]
    
    _clientattrs = app.PTopWindowBase._clientattrs + ('actionflags',
        'large_icons', 'show_labels', 'queryonexit',
        'statuswidgets', 'widgetspecs')
    
    def __init__(self, parent, cls=None):
        # We don't call up to PTopWindowBase.__init__ here
        # because we want to do things in a slightly
        # different order when there are more frills
        
        self.shown = False
        self.actions = {}
        self.app = parent
        
        self._set_client_class(cls)
        
        self._setup_aboutdata()
        self._setup_prefsdata()
        
        self.set_caption(self.defaultcaption)
        self.menu = self.createmenu()
        self.toolbar = self.createtoolbar()
        self.statusbar = self.create_statusbar()
        self.createactions()
        
        if self.messageboxclass is not None:
            self.messagebox = self.messageboxclass(self)
        if self.filedialogclass is not None:
            self.filedialog = self.filedialogclass(self)
        
        self.clientwidget = self.createclient()
        self.editor = self.geteditor()
        self.prefsdialog = self.createprefsdialog()
        
        self.connectaction(ACTION_ABOUT, self.about)
        self.connectaction(ACTION_ABOUTTOOLKIT, self.about_toolkit)
        self.connectaction(ACTION_EXIT, self.exit)
    
    def geteditor(self):
        """Get the proper editor object.
        """
        
        if self.editorclass is not None:
            if self.editorclass is self.clientwidgetclass:
                # This shouldn't normally happen (since the client widget gets
                # checked below to see if it's an editor), but we leave a
                # check here just in case
                return self.clientwidget
            # This typically happens when the editor is a "helper" object
            return self.editorclass(
                mainwidget=self, control=self.clientwidget)
        
        # This typically happens when the editor is a mixin class, either to
        # the client widget or to the main window itself
        for obj in (self.clientwidget, self):
            if PEditor in obj.__class__.__mro__:
                return obj
        return None
    
    def createmenu(self):
        """Create the main window's menu.
        """
        
        if (self.menuclass is not None) and self.actionflags:
            return self.menuclass(self)
        return None
    
    def createtoolbar(self):
        """Create the main window's toolbar.
        """
        
        if (self.toolbarclass is not None) and self.actionflags:
            return self.toolbarclass(self)
        return None
    
    def create_statusbar(self):
        """Create the main window's status bar.
        """
        
        if self.statusbarclass is not None:
            return self.statusbarclass(self, self.statuswidgets)
        return None
    
    def action_exists(self, key):
        """Return True if action key is in our list of actions.
        """
        return (key in self.actionflags)
    
    def _create_action(self, key):
        """Return an action object for key.
        """
        return self.actionclass(key, self)
    
    def createactions(self):
        """Create actions and link them to menu and toolbar items.
        """
        
        lastkey = 0
        for key in actionkeylist:
            if self.action_exists(key):
                if switchedgroup(lastkey, key) and (self.toolbar is not None):
                    self.toolbar.add_separator()
                self.actions[key] = self._create_action(key)
                lastkey = key
    
    def connectaction(self, key, target):
        """Connect action matching key to target method.
        """
        
        if self.action_exists(key):
            self.actions[key].connect_to(target)
    
    def _update_action(self, key, flag):
        """Update action enable state based on flag.
        """
        
        if self.action_exists(key):
            self.actions[key].enable(flag)
    
    def _update_actions(self, editable, pending, modified):
        """Standard enable/disable logic for buttons.
        """
        
        statelist = [
            (self.editlist, editable),
            (self.pendinglist, pending),
            (self.modifiedlist, modified) ]
        for keylist, flag in statelist:
            for key in keylist:
                self._update_action(key, flag)
    
    def updateactions(self):
        """Update action states.
        """
        
        if self.shown and (self.editor is not None):
            self._update_actions(self.editor.editable,
                self.editor.pending, self.editor.modified)
    
    def menuheight(self):
        return self.menu.preferred_height()
    
    def toolbarheight(self):
        return self.toolbar.preferred_height()
    
    def statusbarheight(self):
        return self.statusbar.preferred_height()
    
    def get_clientsize(self):
        h = self.clientwidget.preferred_height()
        if self.menu is not None:
            h += self.menuheight()
        if self.toolbar is not None:
            h += self.toolbarheight()
        if self.statusbar is not None:
            h += self.statusbarheight()
        w = 0
        for widget in (self.clientwidget, self.toolbar):
            w = max(w, widget.preferred_width())
        return (w, h)
    
    def show_init(self):
        """Should always call from derived classes to ensure proper setup.
        """
        
        app.PTopWindowBase.show_init(self)
        self.updateactions()
    
    def getfiledialog(self, path="", filter="", action=ACTION_FILEOPEN):
        if action == ACTION_FILEOPEN:
            return self.filedialog.openfiledialog(path, filter)
        if action == ACTION_FILESAVEAS:
            return self.filedialog.savefiledialog(path, filter)
        return ""
    
    def editorcanclose(self):
        """Return true if the editor can close.
        """
        
        return (self.editor is None) or (self.editor.canclose())
    
    def queryexit(self):
        """Ask user whether to exit program.
        """
        
        return self.messagebox.query2("Application Exit",
            "Exit %s?" % self.get_basename()) # FIXME: use the app name here
    
    def acceptclose(self):
        """Return False if window should not close based on current state.
        """
        
        accept = self.clientcanclose() and self.editorcanclose()
        if accept and (self.app.mainwin is self):
            accept = ((not self.queryonexit) or 
                (self.queryexit() == answerOK))
        return accept

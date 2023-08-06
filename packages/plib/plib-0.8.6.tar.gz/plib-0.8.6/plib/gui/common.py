#!/usr/bin/env python
"""
Module COMMON -- Python GUI Common Global Objects
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common global objects for
the GUI sub-package. These are provided in a separate
module so that, if desired, these objects can be
mutated prior to instantiating your GUI application
(that is, prior to calling gui.runapp() to create
your application, or instantiating your own GUI
application class manually). These objects should
not be mutated after your application is running
because they are used on initialization to create
menu items, toolbar buttons, and actions, and after
that they must remain unchanged.
"""

import sys
import os.path
from functools import partial

from plib.stdlib.systools import plibpath

from plib.gui.defs import *
from plib.gui._toolkit import toolkit

# list of 'automagically connected' signals (meaning that to catch
# them you have to override a method instead of calling setup_notify
# to have the signal sent to you)
automagic_signals = [SIGNAL_QUERYCLOSE, SIGNAL_BEFOREQUIT]

# useful combinations of action constants
ACTIONS_FILE = [
    ACTION_FILENEW, ACTION_FILEOPEN, ACTION_FILESAVE, ACTION_FILESAVEAS,
    ACTION_FILECLOSE]
ACTIONS_FILEMENU = ACTIONS_FILE + [ACTION_EXIT]
ACTIONS_EDIT = [
    ACTION_EDITUNDO, ACTION_EDITREDO,
    ACTION_EDITCUT, ACTION_EDITCOPY, ACTION_EDITPASTE,
    ACTION_EDITDELETE, ACTION_EDITSELECTALL]
ACTIONS_ACTION = [
    ACTION_VIEW, ACTION_EDIT,
    ACTION_OK, ACTION_CANCEL,
    ACTION_REFRESH, ACTION_ADD, ACTION_REMOVE,
    ACTION_APPLY, ACTION_COMMIT, ACTION_ROLLBACK]
ACTIONS_OPTIONS = [ACTION_PREFS]
ACTIONS_OTHER = [
    ACTION_PREFS,
    ACTION_ABOUT, ACTION_ABOUTTOOLKIT,
    ACTION_EXIT]
ACTIONS_HELP = [ACTION_ABOUT, ACTION_ABOUTTOOLKIT]

# action dictionary
actiondict = {
    ACTION_FILENEW: ["filenew", "&New"],
    ACTION_FILEOPEN: ["fileopen", "&Open"],
    ACTION_FILESAVE: ["filesave", "&Save"],
    ACTION_FILESAVEAS: ["filesaveas", "Save &As"],
    ACTION_FILECLOSE: ["fileclose", "&Close"],
    ACTION_VIEW: ["view", "&View"],
    ACTION_EDIT: ["button_edit", "&Edit"],
    ACTION_EDITUNDO: ["editundo", "&Undo"],
    ACTION_EDITREDO: ["editredo", "&Redo"],
    ACTION_EDITCUT: ["editcut", "Cu&t"],
    ACTION_EDITCOPY: ["editcopy", "&Copy"],
    ACTION_EDITPASTE: ["editpaste", "&Paste"],
    ACTION_EDITDELETE: ["editdelete", "&Delete"],
    ACTION_EDITSELECTALL: ["selectall", "Se&lect All"],
    ACTION_REFRESH: ["button_refresh", "Re&fresh"],
    ACTION_ADD: ["button_add", "A&dd"],
    ACTION_REMOVE: ["button_remove", "Remo&ve"],
    ACTION_APPLY: ["apply", "Appl&y"],
    ACTION_COMMIT: ["commit", "Co&mmit"],
    ACTION_ROLLBACK: ["rollback", "Rollbac&k"],
    ACTION_OK: ["button_ok", "&Ok"],
    ACTION_CANCEL: ["button_cancel", "&Cancel"],
    ACTION_PREFS: ["prefs", "&Preferences..."],
    ACTION_ABOUT: ["about", "A&bout..."],
    ACTION_ABOUTTOOLKIT: ["about_toolkit", "About &%s..." %
        toolkit.strip('4')],
    ACTION_EXIT: ["exit", "E&xit"]
}

# action key list (needed to ensure proper ordering of actions,
# since the dictionary keys won't necessarily be ordered)
# TODO: make this dynamically update if actiondict is changed on the fly

actionkeylist = None


def update_actionkeylist():
    global actionkeylist
    actionkeylist = sorted(actiondict.keys())

update_actionkeylist()

# menu key groups (needed to properly sort and arrange menus)
menukeygroups = [
    ("&File", ACTIONS_FILEMENU),
    ("&Edit", ACTIONS_EDIT),
    ("Ac&tion", ACTIONS_ACTION),
    ("&Options", ACTIONS_OPTIONS),
    ("&Help", ACTIONS_HELP) ]


def keymenu(key):
    for title, items in menukeygroups:
        if key in items:
            return title
    return None


# button key group list (for use in adding separators)
buttonkeygroups = [ACTIONS_FILE, ACTIONS_EDIT, ACTIONS_ACTION, ACTIONS_OTHER]


# utility functions to work with key "groups"

def keygroup(key):
    for group in buttonkeygroups:
        if key in group:
            return group
    return None


def switchedgroup(lastkey, key):
    return (lastkey != 0) and (keygroup(lastkey) != keygroup(key))


# utility functions to get fully qualified pixmap path name

_pxdir = os.path.realpath(os.path.join(plibpath, "gui", "_images"))


def pxname(aname, asuffix=None):
    if asuffix:
        return "%s-%s.png" % (aname, asuffix)
    return aname


# Return the fully qualified path name for a px file in the plib directory

def pxfile(aname):
    for asuffix in (toolkit.lower(), sys.platform, os.name, None):
        result = os.path.join(_pxdir, pxname(aname, asuffix))
        if os.path.isfile(result):
            return result
    return pxname(aname)


# Process font arguments to ensure all are filled in

def font_args(widget, font_name, font_size, bold, italic):
    if font_name is None:
        font_name = widget.get_font_name()
    if font_size is None:
        font_size = widget.get_font_size()
    if bold is None:
        bold = widget.get_font_bold()
    if italic is None:
        italic = widget.get_font_italic()
    return font_name, font_size, bold, italic


# Convenience functions to get/set elements of the actiondict

def action_caption(action):
    return actiondict[action][1]


def set_action_caption(action, caption):
    actiondict[action][1] = caption


def action_icon(action):
    return pxfile(actiondict[action][0])


def add_action(action, icon, caption, group=None, index=None, update=True):
    if group is not None:
        if index is None:
            fn = group.append
        else:
            fn = partial(group.insert, index)
        fn(action)
    actiondict[action] = [icon, caption]
    if update:
        update_actionkeylist()


def add_actions(actions, update=True):
    for action_spec in actions:
        kw = dict(update=False)  # hack to avoid syntax error
        add_action(*action_spec, **kw)
    if update:
        update_actionkeylist()

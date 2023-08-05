#!/usr/bin/env python
"""
Module DIALOGS -- Dialog Classes for GUI
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines dialogs for use with PLIB.GUI applications. The
PDialogBase class implements the core functionality to
make it easy to integrate a dialog with a PLIB.GUI
application. The following specific dialogs are also
included:

- PPrefsDialog: automatically constructs a dialog to
  allow editing of the preferences stored in a PIniFile.
"""

from plib.stdlib.ini.defs import *

from plib.gui import main as gui
from plib.gui import specs
from plib.gui.defs import *

# NOTE: I tried using "actual" dialog classes for this
# (e.g., qt.QDialog), but found weird behavior with the
# automated GUI generation code; so for now it's easier
# just to use PTopWindow and specialize it for dialogs.
# The only function this takes away (until I see a need
# to figure out how to do it) is modal dialogs--any dialog
# using this code will be modeless. For the use cases I'm
# interested in, that's not an issue; YMMV.


class PDialogBase(gui.PBaseWindow):
    """Base class for dialogs.
    
    Base class for dialogs; assumes that self.defs
    exists and contains a list of control definitions
    for use by a PAutoPanel. Provides the showdialog
    method to construct the controls (if not already
    constructed) and show the dialog; provides the
    hidedialog method to be linked to buttons in the
    dialog that should hide it.
    """
    
    defaultcaption = "Dialog"
    placement = (SIZE_CLIENTWRAP, MOVE_CENTER)
    
    def __init__(self, parent, panelclass):
        self._dirty = False
        self._modified = False
        gui.PBaseWindow.__init__(self, parent, panelclass)
        
        # Catch the main window closing signal so we can close ourselves
        # (some GUI toolkits don't actually require this, but we do it in
        # all cases for safety and tidiness)
        parent.setup_notify(SIGNAL_CLOSING, self.closedialog)
    
    def _populate_data(self):
        """Populate the dialog with data.
        """
        pass
    
    def _retrieve_data(self):
        """Retrieve data from the dialog.
        """
        pass
    
    def data_changed(self):
        """Widget change signals should call this method.
        """
        self._dirty = True
    
    def showdialog(self):
        """Populate dialog with data, then show it.
        """
        self._populate_data()
        if self.shown:
            self._show_window()
        else:
            self.show_init()
    
    def hidedialog(self):
        """Hide dialog (but don't destroy).
        """
        self._hide_window()
    
    def closedialog(self):
        """Close dialog.
        """
        self.exit()
    
    def button_apply(self):
        """Retrieve dialog data, but keep open.
        """
        if self._dirty:
            self._retrieve_data()
            self._dirty = False
            self._modified = True
    
    def button_ok(self):
        """Retrieve dialog data, then hide it.
        """
        self.button_apply()
        self.hidedialog()
    
    def button_cancel(self):
        """Revert dialog data to original, then hide it.
        """
        if self._dirty:
            self._populate_data()
            self._dirty = False
        self.hidedialog()


# FIXME: Make this code re-entrant, so multiple instances can use this
# same module (the obvious thing is to make the items below into class
# attributes, but doing that seems to break the automatic reading of
# INI file section/option names into variables)

PrefsSections = [] # this will be filled in dynamically by PPrefsDialog

PrefsButtonPanel = [
    specs.get_padding('buttons'),
    specs.get_action_button(ACTION_APPLY, 'button_apply'),
    specs.get_action_button(ACTION_OK),
    specs.get_action_button(ACTION_CANCEL) ]


class PPrefsPanel(gui.PAutoPanel):
    """Preferences dialog top-level panel.
    
    Panel to serve as the overall "frame" of the preferences dialog.
    The _childlist class field should be modified by PPrefsDialog before
    instantiating this class.
    """
    
    childlist = [
        specs.get_toplevel_panel(PrefsButtonPanel,
            ALIGN_BOTTOM, LAYOUT_HORIZONTAL, 'buttons') ]
    
    def __init__(self, parent):
        gui.PAutoPanel.__init__(self, parent, layout=LAYOUT_VERTICAL,
            margin=specs.framemargin, spacing=specs.panelspacing)


# Subclass dialog controls to add generic get_value and set_value methods

class PPrefsCheckBox(gui.PCheckBox):
    
    def get_value(self):
        return self.checked
    
    def set_value(self, value):
        self.checked = value


class PPrefsComboBox(gui.PComboBox):
    
    def get_value(self):
        return self.current_text()
    
    def set_value(self, value):
        self.set_current_text(value)


class PPrefsEditBox(gui.PEditBox):
    
    def get_value(self):
        return self.edit_text
    
    def set_value(self, value):
        self.edit_text = value


class PPrefsNumEditBox(gui.PEditBox):
    
    def get_value(self):
        return int(self.edit_text)
    
    def set_value(self, value):
        self.edit_text = str(value)


# Map data types to appropriate controls

controltypes = {
    INI_INTEGER: [PPrefsNumEditBox,
        (),
        {'expand': False, 'geometry': specs.numeditgeometry()}],
    INI_BOOLEAN: [PPrefsCheckBox,
        (),
        {}],
    INI_STRING: [PPrefsEditBox,
        (),
        {'geometry': specs.editgeometry()}] }


# Utility function to return INI option panel spec

def get_ini_panel(otype, label, name, target):
    klass, args, kwargs = controltypes[otype]
    kwargs['target'] = target
    if otype == INI_BOOLEAN:
        kwargs['caption'] = label
    result = [(klass, args, kwargs, name)]
    if otype != INI_BOOLEAN:
        result.insert(0, specs.get_label(label, name))
    return specs.get_interior_panel(result,
        ALIGN_TOP, LAYOUT_HORIZONTAL, name)


class PPrefsDialog(PDialogBase):
    """Auto-constructing preferences dialog.
    
    Preferences dialog: takes a parent PMainWindow and
    a PIniFile; constructs a dialog for editing the
    options in the PIniFile, and adds an action to the
    PMainWindow to display the dialog.
    """
    
    defaultcaption = "Preferences"
    panelclass = PPrefsPanel
    
    def __init__(self, parent, inifile, labels, style=SECTION_TAB):
        self._inifile = inifile
        self._labels = labels
        self._style = style
        self.data_map = {}
        
        if hasattr(parent, 'defaultcaption'):
            self.defaultcaption = "%s %s" % (
                parent.defaultcaption, self.defaultcaption)
        
        # Build the specs from the INI file
        self.spec_sections(PrefsSections)
        
        # Now get the appropriate widget for the main panel and patch it in
        if style == SECTION_GROUPBOX:
            PrefsMainPanel = PrefsSections
        else:
            PrefsMainPanel = [
                specs.get_tabwidget(PrefsSections, 'main') ]
        self.panelclass.childlist.insert(0,
            specs.get_toplevel_panel(PrefsMainPanel,
                ALIGN_JUST, LAYOUT_VERTICAL, 'main'))
        
        # This will now construct the dialog based on the specs
        PDialogBase.__init__(self, parent, self.panelclass)
        
        # Connect the main window's prefs action to show our dialog
        # (note that this only works if the main window is our parent
        # and it's a PMainWindow--otherwise this connection has to
        # be made by hand after construction)
        if hasattr(parent, 'connectaction'):
            if hasattr(parent, 'preferences'):
                # This should be the normal case
                target = parent.preferences
            else:
                # This is here in case an alternate main window
                # class is in use that has a connectaction method
                # but not a preferences method
                target = self.showdialog
            parent.connectaction(ACTION_PREFS, target)
        
        # TODO: Fix sizing in wx
    
    def showdialog(self):
        """Populate dialog with data, then show it.
        
        Note that if our parent is a PTopWindow that is storing
        its coordinates in settings, we have to update the
        settings variables first so the shown dialog will reflect
        the current state.
        """
        if self._parent:
            self._parent.get_coordinates()
        PDialogBase.showdialog(self)
    
    def button_apply(self):
        """Retrieve dialog data, but keep open.
        
        Note that if our parent is a PTopWindow that is storing
        its coordinates in settings, and.
        """
        PDialogBase.button_apply(self)
        if self._parent:
            self._parent.set_coordinates()
    
    def closedialog(self):
        """Save preferences if modified.
        """
        if self._modified:
            self._inifile.writeini()
        PDialogBase.closedialog(self)
    
    def _iterate_data(self, scallback, ocallback):
        if scallback is None:
            # We're populating or retrieving, need the actual panel widget
            main = self.clientwidget
        else:
            # We're specifying, need the spec list
            main = self._groups
        inifile = self._inifile
        labels = self._labels
        
        for sname, opts in inifile._optionlist:
            if scallback is not None:
                scallback(main, inifile, labels, sname)
            for opt in opts:
                attrname = getter = setter = None
                if len(opt) > 4:
                    oname, otype, odefault, getter, setter = opt
                elif len(opt) > 3:
                    oname, otype, odefault, attrname = opt
                else:
                    oname, otype, odefault = opt
                if attrname is None:
                    attrname = "%s_%s" % (sname, oname)
                if ocallback is not None:
                    ocallback(main, inifile, labels, attrname,
                        otype, getter, setter)
            if scallback is not None:
                scallback(main, inifile, labels, sname, True)
        
        if (scallback is not None) and (self._style == SECTION_GROUPBOX):
            self._groups.append(specs.get_padding('end'))
    
    def _current(self):
        if self._style == SECTION_GROUPBOX:
            return self._currentgroup[1][1]
        else:
            return self._currentgroup[1][0]
    
    def _spec_section(self, groups, inifile, labels, sname, done=False):
        # Add panel or group for INI file section
        if done:
            self._current().append(specs.get_padding(sname))
            if self._currentgroup is not None:
                groups.append(self._currentgroup)
        else:
            if self._style == SECTION_GROUPBOX:
                self._currentgroup = specs.get_groupbox([],
                    labels[sname], sname)
            else:
                self._currentgroup = (labels[sname],
                    specs.get_tab_panel([],
                        ALIGN_TOP, LAYOUT_VERTICAL, sname))
    
    def _spec_option(self, groups, inifile, labels, attrname,
            otype, getter, setter):
        # Add individual INI file option to current panel/section
        self._current().append(get_ini_panel(otype,
            labels[attrname], attrname, self.data_changed))
    
    def spec_sections(self, groups):
        """Generate the specs for the main panel from the INI file.
        """
        self._groups = groups
        self._currentgroup = None
        self._iterate_data(self._spec_section, self._spec_option)
        del self._currentgroup
        del self._groups
    
    def _populate_option(self, mainpanel, inifile, labels, attrname,
            otype, getter, setter):
        # Populate control for INI file option
        control = getattr(mainpanel, attrname)
        if getter is not None:
            value = getter()
        else:
            value = getattr(inifile, attrname)
        control.set_value(value)
    
    def _populate_data(self):
        """Populate dialog data from PIniFile object.
        """
        self._iterate_data(None, self._populate_option)
    
    def _retrieve_option(self, mainpanel, inifile, labels, attrname,
            otype, getter, setter):
        # Get GUI value for INI file option
        control = getattr(mainpanel, attrname)
        value = control.get_value()
        if setter is not None:
            setter(value)
        else:
            setattr(inifile, attrname, value)
    
    def _retrieve_data(self):
        """Set PIniFile options from dialog data.
        """
        self._iterate_data(None, self._retrieve_option)

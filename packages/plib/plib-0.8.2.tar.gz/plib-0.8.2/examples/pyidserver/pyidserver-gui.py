#!/usr/bin/env python
"""
PYIDSERVER-GUI.PY
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

GUI for Python implementation of IDServer. See
PYIDSERVER.PY for more information about the basic
"engine" involved. This GUI overlay to the engine is
intended to demonstrate some key features of the
``plib.gui`` sub-package, as well as the general Unix
programming model of "build a base engine first, which
can be driven by a rudimentary command-line interface;
then build a GUI on top of it." The program also shows
how to multiplex a GUI with socket events.

Key features:

  - The ``plib.gui.specs`` module is used to define
    the entire GUI in terms of Python lists and tuples.
    The only actual code involved is some setup after
    the GUI controls are instantiated, and the event
    handlers for the specific control events.
  
  - The event handlers themselves are "automagically"
    bound to their control event signals. This is done
    by making the name of the event handler bear a
    predictable relationship to the name of the control
    itself. The underlying code in the ``gui.PMainPanel``
    class then does the method lookups involved and
    binds the control signals to their targets. See the
    comments in the GUI spec definitions.
  
  - The GUI event loop and the socket I/O required for
    idserver are multiplexed; even if it takes some time
    for the remote server to respond with data, the GUI
    remains responsive, with no code required other than
    mixing in the ``NotifierClient`` class (we do add
    a few lines of code to the derived class to enable
    us to stop a query in progress from the GUI, but
    that is extra functionality; the multiplexing itself
    would work fine without it).
"""

import os

from plib import __version__

from plib.stdlib import version

from plib.gui import main as gui
from plib.gui import common
from plib.gui.defs import *

CAPTION_GO = "&Go"
ICON_GO = common.action_icon(ACTION_OK)
CAPTION_STOP = "&Stop"
ICON_STOP = common.action_icon(ACTION_CANCEL)
common.set_action_caption(ACTION_OK, CAPTION_GO)

from plib.gui import specs
specs.mainwidth = 400
specs.mainheight = 300
del specs
from plib.gui.specs import *

import pyidserver


# Monkeypatch idserver to multiplex with GUI event loop
# and add the ability to stop the query in progress

_old_chat_replies = pyidserver.chat_replies

class chat_replies(gui.NotifierClient, _old_chat_replies):
    
    instance = None
    
    def __init__(self, addr, items, callback=None):
        _old_chat_replies.__init__(self, addr, items, callback)
        chat_replies.instance = self
    
    def close(self):
        chat_replies.instance = None
        super(chat_replies, self).close()

pyidserver.chat_replies = chat_replies


class IDServerFrame(gui.PMainPanel):
    
    aboutdata = {
        'name': "PyIDServer",
        'version': version.version_string(__version__),
        'copyright': "Copyright (C) 2008-2012 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'description': "A Python GUI for IDServer", 
        'developers': ["Peter Donis"],
        'website': "http://www.peterdonis.net",
        'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0],
            "pyidserver.png") }
    
    maintitle = "PyIDServer"
    
    layout = LAYOUT_VERTICAL
    placement = (SIZE_CLIENTWRAP, MOVE_CENTER)
    
    childlist = [
        toplevel_panel(ALIGN_TOP, LAYOUT_HORIZONTAL, 'top', [
            interior_panel(ALIGN_JUST, LAYOUT_HORIZONTAL, 'left', [
                # No standard event handler for this edit box (the signal
                # we want to bind to, the Enter key, isn't the standard
                # one for an edit box, so we'll do the binding by hand
                # below); note that the automatic lookup code for event
                # handlers (see below) does nothing if no matching handler
                # is found (this makes declaring the GUI a lot easier since
                # you don't have to duplicate knowledge of which controls
                # have handlers, just declare the ones you want as methods)
                editbox('url') ]),
            interior_panel(ALIGN_RIGHT, LAYOUT_HORIZONTAL, 'right', [
                # This action button has a non-standard name, so we have to
                # specify it; the ``go`` method of the main panel then becomes
                # the target (buttons and action buttons are the only spec
                # controls that automatically assume they have targets; this
                # seems reasonable since that's what buttons are for)
                action_button(ACTION_OK, 'go') ]) ]),
        toplevel_panel(ALIGN_JUST, LAYOUT_VERTICAL, 'main', [
            midlevel_panel(ALIGN_TOP, LAYOUT_HORIZONTAL, 'header', [
                toplevel_panel(ALIGN_LEFT, LAYOUT_HORIZONTAL, 'controls', [
                    # Each control below will automatically look for its
                    # event handler; the target method for check boxes is
                    # ``<name>_check``, where ``<name>`` is the base name of
                    # the control (the 2nd parameter)--note that in the specs
                    # code the actual full name of the control will be
                    # ``checkbox_<name>``, to avoid name collisions between
                    # controls of different types; for the combo box, the
                    # handler method name will be ``<name>_selected``
                    checkbox("DNS Only", 'dnsonly'),
                    checkbox("Set Protocol", 'protocol'),
                    combobox('protocol',
                        sorted(pyidserver.protocols.iterkeys())),
                    checkbox("Set Port", 'portnum'),
                    # No handler for the numedit, just need to keep it at a
                    # fixed size
                    numeditbox('portnum', expand=False) ]),
                padding('main') ]),
            interior_panel(ALIGN_JUST, LAYOUT_VERTICAL, 'body', [
                # No event handler for the text control (since it's
                # display-only anyway)
                textcontrol('output') ]) ]),
        toplevel_panel(ALIGN_BOTTOM, LAYOUT_HORIZONTAL, 'bottom', [
            padding('bottom'),
            # These action buttons all have their standard names, so no
            # additional parameters are needed; each one's target will be the
            # method with its name: ``about``, ``about_toolkit``, and
            # ``exit`` (note that the ``exit`` method is in the parent, which
            # is the main window, not the main panel itself; the automatic
            # lookup method finds it by traversing the parent tree if the
            # method is not found in the panel)
            action_button(ACTION_ABOUT),
            action_button(ACTION_ABOUTTOOLKIT),
            action_button(ACTION_EXIT) ]) ]
    
    query_in_progress = False
    
    def _createpanels(self):
        # Create child widgets
        super(IDServerFrame, self)._createpanels()
        
        # The function we're wrapping with our GUI, and its default parameters
        self.func = pyidserver.run_main
        
        # Controls affected by the DNS Only checkbox
        self.dnsonly_controls = (
            (self.checkbox_protocol, self.combo_protocol),
            (self.checkbox_portnum, self.edit_portnum) )
        
        # Controls independent of DNS Only checkbox
        self.other_controls = (
            self.edit_url, self.checkbox_dnsonly)
        
        # Adjust some widget parameters that couldn't be set in constructors
        self.edit_url.setup_notify(SIGNAL_ENTER, self.go)
        
        self.checkbox_dnsonly.checked = self.default_dnsonly()
        self.dnsonly_check() # technically not needed, put in for completeness
        
        self.combo_protocol.set_current_text(
            self.default_protocol() or pyidserver.PROTO_DEFAULT)
        self.protocol_check()
        
        self.edit_portnum.edit_text = str(self.default_portnum())
        self.portnum_check()
        
        self.text_output.set_font("Courier New")
        
        # Set up output file-like object here for convenience
        self.outputfile = gui.PTextFile(self.text_output)
        
        # Start with keyboard focus in the URL text entry
        self.edit_url.set_focus()
    
    def default_dnsonly(self):
        return self.func.func_defaults[2]
    
    def default_protocol(self):
        return self.func.func_defaults[3]
    
    def default_portnum(self):
        return self.func.func_defaults[4]
    
    def dnsonly_check(self):
        """Called when the dns_only checkbox is checked/unchecked.
        
        Only enable protocol and port controls if not DNS only.
        """
        
        enable = not self.checkbox_dnsonly.checked
        for ctrl, subctrl in self.dnsonly_controls:
            ctrl.enabled = enable
            subctrl.enabled = enable and ctrl.checked
    
    def protocol_check(self):
        """Called when the protocol checkbox is checked/unchecked.
        
        Sync protocol combo enable with check box."""
        self.combo_protocol.enabled = self.checkbox_protocol.checked
    
    def protocol_selected(self, index):
        """Called when a protocol combo selection is made.
        
        For now, just prints a diagnostic showing the signal response.
        """
        print index, self.combo_protocol[index]
    
    def portnum_check(self):
        """Called when the portnum checkbox is checked/unchecked.
        
        Sync portnum edit enable with check box.
        """
        self.edit_portnum.enabled = self.checkbox_portnum.checked
    
    def go(self):
        """Called when the Go/Stop button is pushed.
        
        Execute the idserver query, or stop a query in progress.
        For executing a query, this method is also called when the
        Enter key is pressed while in the URL edit box.
        """
        
        if self.query_in_progress:
            # Shut down the async I/O
            chat_replies.instance.close()
        
        else:
            # Clear output
            self.outputfile.truncate(0)
            
            # Check URL
            url = self.edit_url.edit_text
            if len(url) < 1:
                self.outputfile.write("Error: No URL entered.")
                self.outputfile.flush()
                return
            
            # Fill in arguments that user selected, if any
            dns_only = self.checkbox_dnsonly.checked
            if self.checkbox_protocol.checked:
                protocol = self.combo_protocol.current_text()
            else:
                protocol = self.default_protocol()
            if self.checkbox_portnum.checked:
                portnum = int(self.edit_portnum.edit_text)
            else:
                portnum = self.default_portnum()
            
            # Now execute
            for ctrl, subctrl in self.dnsonly_controls:
                ctrl.enabled = subctrl.enabled = False
            for ctrl in self.other_controls:
                ctrl.enabled = False
            self.button_go.set_caption(CAPTION_STOP)
            self.button_go.set_icon(ICON_STOP)
            self.query_in_progress = True
            
            self.func(url, outfile=self.outputfile,
                dns_only=dns_only, protocol=protocol, portnum=portnum)
        
        # Either we're done, or we've stopped a query in progress
        self.query_in_progress = False
        self.button_go.set_caption(CAPTION_GO)
        self.button_go.set_icon(ICON_GO)
        for ctrl in self.other_controls:
            ctrl.enabled = True
        self.dnsonly_check()


if __name__ == "__main__":
    # Our client frame will be wrapped in a ``PTopWindow``
    gui.runapp(IDServerFrame)

#!/usr/bin/env python
"""
Module PANEL -- GUI Table Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for panel widgets.
"""

from plib.gui.defs import *


class PPanelBase(object):
    """Base class for 'panel' widget.
    
    The panel widget is a container for laying out
    other widgets. The layout parameter is used to
    determine whether child widgets are laid out
    horizontally or vertically; the align parameter
    determines how this panel takes up space in its
    parent widget. Panels should be nestable to any
    depth desired, to enable complex layouts.
    
    For best results, the creation of child widgets
    (including child panels) should be done by
    overriding the _createpanels method and doing
    it there. Child panels simply need to be passed
    the parent panel in their constructors in order
    to be automatically included in the parent panel's
    sizing; other child widgets may need to manually
    add themselves by calling _addwidget. If child
    creation is not done in _createpanels, then the
    _dolayout method must be called manually after the
    child widgets have been created and added.
    
    Note also that there is currently no checking
    done to ensure that the align value of a panel
    makes sense when combined with the alignment of
    its sibling widgets and the layout of its parent
    widget (for example, an ALIGN_TOP or ALIGN_BOTTOM
    panel with ALIGN_LEFT or ALIGN_RIGHT siblings
    inside a LAYOUT_HORIZONTAL parent panel). It is
    up to the caller to ensure that the combined
    parameters make sense. (This also applies to the
    order in which child widgets are added -- for
    example, an ALIGN_LEFT widget must be added
    before an ALIGN_JUST widget in a horizontal
    layout, or the ALIGN_LEFT widget will be on the
    right.)
    """
    
    def __init__(self, parent,
        layout=LAYOUT_NONE, style=PANEL_NONE, align=ALIGN_JUST,
        margin=-1, spacing=-1, width=-1, height=-1):
        
        self._parent = parent
        self._layout = layout
        self._align = align
        self._style = style
        
        if (width > -1) or (height > -1):
            self.set_min_size(width, height)
        if (margin > -1):
            self.set_margin(margin)
        if (spacing > -1):
            self.set_spacing(spacing)
        
        # Create child panels, if any, and do layout if children were created
        self._panels = []
        self._createpanels()
        self._dolayout()
        
        # Add ourselves to parent panel if applicable
        if hasattr(parent, '_addpanel'):
            parent._addpanel(self)
    
    def _addwidget(self, widget):
        # Derived classes may override to do any necessary
        # adjustment when a widget is added.
        pass
    
    def _addpanel(self, panel):
        self._panels.append(panel)
        self._addwidget(panel)
    
    def _createpanels(self):
        # Derived classes should override to create
        # child panels, if any.
        pass
    
    def _dolayout(self):
        # Derived classes should override to do any
        # necessary creation of physical layout objects
        # after all child panels are created.
        pass
    
    def set_min_size(self, width, height):
        """Derived classes must implement.
        """
        raise NotImplementedError
    
    def set_margin(self, margin):
        """Derived classes must implement.
        """
        raise NotImplementedError
    
    def set_spacing(self, spacing):
        """Derived classes must implement.
        """
        raise NotImplementedError

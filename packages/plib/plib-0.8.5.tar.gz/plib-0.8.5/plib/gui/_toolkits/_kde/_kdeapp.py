#!/usr/bin/env python
"""
Module KDEAPP -- Python KDE Application Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI application objects.
"""

import sys

import qt
import kdecore
import kdeui

from plib.gui.defs import *
from plib.gui._base import app

from _kdecommon import _PKDECommunicator

# We'll need this for the about dialog hackery below

_kdeversion_items = tuple(map(
    lambda name: getattr(kdecore.KDE, 'version%s' % name)(),
    ('Major', 'Minor', 'Release')))


def _kdeabout(name, version):
    return kdecore.KAboutData(name, name, version)


def _kdeparse(aboutdata):
    data = _kdeabout(aboutdata['name'], aboutdata['version'])
    data.setCopyrightStatement(aboutdata['copyright'])
    data.setLicenseText(aboutdata['license'])
    data.setShortDescription(aboutdata['description'])
    for dev in aboutdata['developers']:
        data.addAuthor(dev)
    data.setHomepage(aboutdata['website'])
    return data


def _kdelogo(icon, kaboutdata):
    qimg = qt.QImage(icon)
    qimg_scaled = qimg.scale(qimg.width() * 2, qimg.height() * 2)
    kaboutdata.setProgramLogo(qimg_scaled)


class _PKDEBaseMixin(kdeui.KMainWindow, _PKDECommunicator):
    """Mixin class for KDE base windows.
    """
    
    _closed = False  # guard to trap close from system menu, see below
    
    def _get_w(self):
        return self.width()
    w = property(_get_w)
    
    def _show_window(self):
        kdeui.KMainWindow.show(self)
    
    def _hide_window(self):
        kdeui.KMainWindow.hide(self)
    
    def set_caption(self, caption):
        self.setPlainCaption(caption)
    
    def _get_desktop_rect(self, primary=True):
        # Correctly handle virtual desktop across multiple screens
        desktop = self.app.desktop()
        l = desktop.x()
        t = desktop.y()
        w = desktop.width()
        h = desktop.height()
        if desktop.isVirtualDesktop() and primary:
            # Return the rect of the primary screen only
            i = desktop.primaryScreen()
            n = desktop.numScreens()
            w = w / n
            # NOTE: We have to check for i > 0 here because in some
            # cases (e.g., when running in a VirtualBox), Qt thinks
            # the desktop is "virtual" but there's only one screen and
            # desktop.primaryScreen returns 0 instead of 1.
            if i > 0:
                l += w * (i - 1)
        else:
            i = 0
            n = 1
        return i, n, l, t, w, h
    
    def sizetoscreen(self, maximized):
        if maximized:
            if self.shown:
                self.showMaximized()
            else:
                self._showMax = True
        else:
            i, n, l, t, w, h = self._get_desktop_rect()
            self.resize(
                w - self.sizeoffset,
                h - self.sizeoffset)
            self.move(l, t)
    
    def sizetoclient(self, clientwidth, clientheight):
        self.resize(clientwidth, clientheight)
    
    def center(self):
        i, n, l, t, w, h = self._get_desktop_rect()
        g = self.frameGeometry()
        x, y = g.width(), g.height()
        self.move(l + (w - x)/2, t + (h - y)/2)
    
    def show_init(self):
        if hasattr(self, '_showMax'):
            self.showMaximized()
            del self._showMax
        else:
            kdeui.KMainWindow.show(self)
    
    def exit(self):
        # Guard traps a close other than from this method, so we don't
        # throw an exception if this method gets called after we close
        # but before shutdown (?? Why isn't this necessary in Qt?)
        if not self._closed:
            self.close()
    
    def closeEvent(self, event):
        # 'automagic' code for SIGNAL_QUERYCLOSE
        if self._canclose():
            self._emit_event(SIGNAL_CLOSING)
            self._closed = True # set guard used above
            event.accept()
        else:
            event.ignore()
    
    def hideEvent(self, event):
        self._emit_event(SIGNAL_HIDDEN)


class PKDEBaseWindow(_PKDEBaseMixin, app.PBaseWindowBase):
    """Customized KDE base window class.
    """
    
    def __init__(self, parent, cls=None):
        _PKDEBaseMixin.__init__(self)
        app.PBaseWindowBase.__init__(self, parent, cls)
        self.setCentralWidget(self.clientwidget)
    
    def show_init(self):
        app.PBaseWindowBase.show_init(self)
        _PKDEBaseMixin.show_init(self)


class _PKDEMainMixin(_PKDEBaseMixin):
    """Mixin class for KDE top windows and main windows.
    """
    
    _aboutdlg = None
    _aboutkde = None
    
    def set_iconfile(self, iconfile):
        self.setIcon(qt.QPixmap(iconfile))
    
    def _size_to_settings(self, width, height):
        self.resize(width, height)
    
    def _move_to_settings(self, left, top):
        self.move(left, top)
    
    def _get_current_geometry(self):
        p = self.pos()
        s = self.size()
        return p.x(), p.y(), s.width(), s.height()
    
    def choose_directory(self, curdir):
        return str(qt.QFileDialog.getExistingDirectory(
            qt.QString(curdir), self, 'select_folder', "Select Folder"))
    
    def about(self):
        # FIXME: segfaults when creating the dialog on some KDE 3.5 versions
        # when used with socket notifier
        if (self.aboutdata is not None):
            kaboutdata = _kdeparse(self.aboutdata)
            if 'icon' in self.aboutdata:
                _kdelogo(self.aboutdata['icon'], kaboutdata)
            kdeui.KAboutApplication(kaboutdata).exec_loop()
    
    def about_toolkit(self):
        # FIXME: segfaults when creating the dialog on some KDE 3.5 versions
        # when used with socket notifier
        kdeui.KAboutKDE().exec_loop()
    
    def closeEvent(self, event):
        # 'automagic' code for SIGNAL_QUERYCLOSE
        if self._canclose():
            self._emit_event(SIGNAL_CLOSING)
            for dlg in (self._aboutdlg, self._aboutkde):
                if dlg is not None:
                    dlg.done(0)
            self._closed = True # set guard used above
            event.accept()
        else:
            event.ignore()


class PKDETopWindow(_PKDEMainMixin, app.PTopWindowBase):
    """Customized KDE top window class.
    """
    
    def __init__(self, parent, cls=None):
        _PKDEMainMixin.__init__(self)
        app.PTopWindowBase.__init__(self, parent, cls)
        self.setCentralWidget(self.clientwidget)
    
    def show_init(self):
        app.PTopWindowBase.show_init(self)
        _PKDEMainMixin.show_init(self)


class PKDEApplication(kdecore.KApplication, app.PApplicationBase,
        _PKDECommunicator):
    """Customized KDE application class.
    """
    
    _in_local_loop = False
    
    def __init__(self, arglist=[], cls=None, use_mainwindow=False):
        if cls is None:
            klass = self.mainwidgetclass
        else:
            klass = cls
        
        if hasattr(klass, 'aboutdata') and (klass.aboutdata is not None):
            aboutdata = klass.aboutdata
        
        elif hasattr(klass, 'clientwidgetclass') and \
                hasattr(klass.clientwidgetclass, 'aboutdata'):
            
            aboutdata = klass.clientwidgetclass.aboutdata
        
        else:
            aboutdata = None
        
        if aboutdata:
            kaboutdata = _kdeparse(aboutdata)
        else:
            kaboutdata = _kdeabout("Unnamed", "0.0")
        
        # All the above because KDE requires this incantation first
        kdecore.KCmdLineArgs.init(kaboutdata)
        kdecore.KApplication.__init__(self)
        app.PApplicationBase.__init__(self, arglist, cls, use_mainwindow)
        self.mainwin = self.createMainWidget()
        self.setMainWidget(self.mainwin)
        
        # 'automagic' signal connection
        self.setup_notify(SIGNAL_BEFOREQUIT, self.before_quit)
    
    def _eventloop(self):
        self.exec_loop()
    
    def process_events(self):
        self.processEvents()
    
    # For use when multiplexing with other event types (e.g.,
    # in a NotifierClient
    
    # FIXME: This only seems to work for KDE 3 when enterLoop() and
    # exitLoop() are called directy from NotifierClient ???
    
    #def enter_yield(self):
    #    if not self._in_local_loop:
    #        self.eventLoop().enterLoop()
    #        self._in_local_loop = True
    
    #def exit_yield(self):
    #    if self._in_local_loop:
    #        self._in_local_loop = False
    #        self.eventLoop().exitLoop()

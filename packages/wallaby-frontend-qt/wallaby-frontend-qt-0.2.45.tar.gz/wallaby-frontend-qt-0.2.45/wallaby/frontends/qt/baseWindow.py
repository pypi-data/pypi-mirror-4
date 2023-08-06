#!/usr/bin/env python
# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.


import wallaby.FX as FX
import wallaby.FXUI as FXUI

from wallaby.qt_combat import *

from wallaby.pf.peer import *
from wallaby.frontends.qt.widgets.baseWidget import *
import wallaby.backends.couchdb as couch
from wallaby.pf.peer.debugger import *
from wallaby.frontends.qt.widgets.wallabyOverlay import *
from wallaby.apps.baseApp import *

from twisted.internet import defer

class BaseWindow(BaseApp, QtGui.QMainWindow):
    def __init__(self, vendorName, appName, options, quitCB, parent=None, dbName=None, embedded=False, *args, **ka):
        BaseApp.__init__(self, quitCB, dbName, embedded=embedded, appName=appName)
        QtGui.QMainWindow.__init__(self, parent)

        self._options = options

        self._embedded = embedded

        # self.setAttribute(QtCore.Qt.WA_MacBrushedMetal)

        if not embedded:
            FX.mainWindow = self
            self.setEnabled(False)

        self._vendorName = vendorName
        self._appName = appName
        self._showOverlay = True

        self._splash = None

        self._settings = QtCore.QSettings(vendorName, appName)

    def settings(self):
        return self._settings

    def configure(self):
        geo = self._settings.value("geometry")
        winState = self._settings.value("windowState")
        if geo is not None: self.restoreGeometry(geo)
        if winState is not None: self.restoreState(winState)

    def setSplash(self, splash):
        self._splash = splash

    def overlayMode(self):
        return not self._showOverlay

    def options(self):
        return self._options

    def hideConfig(self):
        if FXUI.configEditor and FXUI.configEditor.isVisible():
            FXUI.configEditor.hide()

    def openConfig(self, widget):
        if FXUI.configEditor == None and (self._options is None or self._options.app != 'inspector'):
            from wallaby.apps.inspector.mainWindow import MainWindow
            FXUI.configEditor = MainWindow(self.hideConfig, self._options, embedded=True)

            if self._options is not None:
                FXUI.configEditor.authenticated(self._options.username, self._options.password, self._options)
            else:
                FXUI.configEditor.authenticated()

        if FXUI.configEditor != None and not FXUI.configEditor.isVisible(): FXUI.configEditor.show()

        from wallaby.pf.peer.documentChanger import DocumentChanger
        from wallaby.pf.peer.tab import Tab
        House.get("__CONFIG__").throw(DocumentChanger.In.Select, ("widgets", widget._template) )
        House.get("__CONFIG__").throw(Tab.In.Select, "main.0")
        if FXUI.configEditor != None: FXUI.configEditor.raise_()
        else: 
            if self._options is None or self._options.app != 'inspector':
                self.toggleOverlay()

    def setDebuggedRooms(self, rooms):
        self._debuggedRooms = rooms

    def keyPressEvent(self, e):

        if e.modifiers() & QtCore.Qt.ControlModifier and e.modifiers() & QtCore.Qt.AltModifier and e.key() == QtCore.Qt.Key_S:
            tl = FXUI.app.topLevelAt(QtGui.QCursor.pos())
            if tl != FXUI.mainWindow: return

            widget = FXUI.app.widgetAt(QtGui.QCursor.pos())

            if widget == None: return
            while not isinstance(widget, BaseWidget): 
                if widget.parent() == None: return
                widget = widget.parent()

            self.openConfig(widget)

        elif e.modifiers() & QtCore.Qt.ControlModifier and e.modifiers() & QtCore.Qt.AltModifier and e.key() == QtCore.Qt.Key_O:
            FXUI.mainWindow.toggleOverlay()
        else:
            QtGui.QMainWindow.keyPressEvent(self, e)

    def toggleOverlay(self):
        widgets = self.findChildren(BaseWidget)
        for w in widgets:
            if self._showOverlay:
                w.showOverlay()
            else: 
                w.hideOverlay()

        WallabyOverlay.resetColors()

        self._showOverlay = not self._showOverlay

    def resizeEvent(self, e):
        QtGui.QMainWindow.resizeEvent(self, e)
        if self.overlayMode():
            widgets = self.findChildren(BaseWidget)
            for w in widgets:
                w.resizeOverlay() 

    def reloadOverlays(self):
        if self.overlayMode():
            widgets = self.findChildren(BaseWidget)
            for w in widgets:
                w.hideOverlay()

            WallabyOverlay.resetColors()

            for w in widgets:
                w.showOverlay()

    def isRunning(self):
        self.setEnabled(True)

        from twisted.internet import reactor
        if self._splash != None: reactor.callLater(0.3, self._splash.finish, self)

    def closeEvent(self, e):
        settings = QtCore.QSettings(self._vendorName, self._appName)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.sync()
        self.quit()
        e.ignore()

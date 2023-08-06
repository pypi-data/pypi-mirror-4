# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FXUI as FXUI

from wallaby.frontends.qt.meta import *
from wallaby.qt_combat import *
from wallaby.pf.peer.tab import *

from container import *

class Tabs(QtGui.QTabWidget, Container):
    __metaclass__ = QWallabyMeta

    identifier = Meta.property("string")
    defaultSheet = Meta.property("string")

    def __init__(self, *args):
        QtGui.QTabWidget.__init__(self, *args)
        Container.__init__(self, *args)

        self._peer = None
        self.currentChanged.connect(self._tabChanged)

    def isMultiPage(self):
        return True

    def overlayRect(self):
        r = BaseWidget.overlayRect(self)
        if self.documentMode():
            r.moveTo(r.x(), self.height())
        else:
            r.moveTo(r.x(), 22)

        r.setHeight(18) 
        return r

    def childCount(self):
        return self.count()

    def addChildWidget(self, w):
        self.addTab(w, w.windowTitle())

    def getChildWidget(self, pos):
        return self.widget(pos)

    def removeChildWidget(self, pos):
        self.removeTab(pos)

    def _tabChanged(self, index):
        containers = self.currentWidget().findChildren(Container)
        for c in containers: c.activate()

        if FXUI.mainWindow and FXUI.mainWindow.overlayMode():
            from twisted.internet import reactor
            reactor.callLater(0, FXUI.mainWindow.reloadOverlays)

    def deregister(self, remove=False):
        if self._peer: self._peer.destroy(remove)
        self._peer = None

    def selectByIndex(self, idx):
        self.setCurrentIndex(idx)

    def selectByName(self, name):
        w = self.findChildren(QtGui.QWidget, name + "Sheet")
        if w != None and len(w) == 1: self.setCurrentWidget(w[0])
        elif self.defaultSheet != None:
            w = self.findChildren(QtGui.QWidget, self.defaultSheet + "Sheet")
            if w != None and len(w) == 1: self.setCurrentWidget(w[0])

    def register(self):
        Container.register(self)
        self._peer = Tab(self.room, self, self.identifier)


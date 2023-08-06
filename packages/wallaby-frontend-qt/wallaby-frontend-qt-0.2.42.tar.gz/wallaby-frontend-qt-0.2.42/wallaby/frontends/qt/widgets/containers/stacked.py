# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.frontends.qt.meta import *
from wallaby.qt_combat import *
from container import *
from wallaby.pf.peer.tab import *

class Stacked(QtGui.QStackedWidget, Container):
    __metaclass__ = QWallabyMeta

    identifier = Meta.property("string")
    defaultSheet = Meta.property("string")

    def __init__(self, *args):
        QtGui.QStackedWidget.__init__(self, *args)
        Container.__init__(self, QtGui.QStackedWidget, *args)

        self._peer = None
        self._sheetPrototypes = {}

        self.currentChanged.connect(self._tabChanged)

    def isMultiPage(self):
        return True

    def childCount(self):
        return self.count()

    def getChildWidget(self, pos):
        return self.widget(pos)

    def addChildWidget(self, w):
        self.addWidget(w)

    def removeChildWidget(self, w):
        self.removeWidget(w)
        w.deleteLater()

    def overlayRect(self):
        r = BaseWidget.overlayRect(self)
        r.moveTo(r.x(), 22)

        r.setHeight(18) 
        return r

    def _tabChanged(self, index):
        if index >= 0:
            containers = self.currentWidget().findChildren(Container)
            for c in containers: c.activate()

            if FX.mainWindow and FX.mainWindow.overlayMode():
                from twisted.internet import reactor
                reactor.callLater(0, FX.mainWindow.reloadOverlays)

    def doSetCurrentIndex(self, idx):
        if self.currentWidget() is not None:
            self.currentWidget().setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)

        self.setCurrentIndex(idx)
        self.currentWidget().setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.adjustSize()

    def selectByIndex(self, idx):
        self.doSetCurrentIndex(idx)

    def selectByName(self, name):
        w = self.findChildren(QtGui.QWidget, name + "Sheet")
        if w != None and len(w) == 1: self.doSetCurrentIndex(self.indexOf(w[0]))
        elif self.defaultSheet != None:
            w = self.findChildren(QtGui.QWidget, self.defaultSheet + "Sheet")
            if w != None and len(w) == 1: self.doSetCurrentIndex(self.indexOf(w[0]))
            

    def deregister(self, remove=False):
        if self._peer: self._peer.destroy(remove)
        self._peer = None

    def register(self):
        Container.register(self)
        self._peer = Tab(self.room, self, self.identifier)

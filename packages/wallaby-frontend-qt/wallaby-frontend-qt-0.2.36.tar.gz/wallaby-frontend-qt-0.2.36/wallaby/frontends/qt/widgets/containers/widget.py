# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *
from container import *

class Widget(QtGui.QWidget, Container):
    __metaclass__ = QWallabyMeta

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        Container.__init__(self, QtGui.QWidget, *args)

        self._sheetPrototypes = {}
        self._layout = None

    def createLayout(self):
        self._layout = QtGui.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        self.setLayout(self._layout)

    def childCount(self):
        if self._layout is None: return 0
        return self._layout.count()

    def getChildWidget(self, pos):
        if self._layout is None: return None
        return self._layout.takeAt(pos).widget()

    def addChildWidget(self, w):
        if self._layout is None: self.createLayout()
        self._layout.addWidget(w)

    def removeChildWidget(self, w):
        Container.removeChildWidget(self, w)

    def overlayRect(self):
        r = BaseWidget.overlayRect(self)
        r.moveTo(r.x(), 22)

        r.setHeight(18) 
        return r

    def deregister(self, remove=False):
        pass

    def register(self):
        Container.register(self)

# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *
from container import *

class GroupBox(QtGui.QGroupBox, Container):
    __metaclass__ = QWallabyMeta

    def __init__(self, *args):
        QtGui.QGroupBox.__init__(self, *args)
        Container.__init__(self, QtGui.QGroupBox, *args)

        self._sheetPrototypes = {}

        self._layout = QtGui.QVBoxLayout()
        self.setLayout(self._layout)

    def childCount(self):
        return self._layout.count()

    def getChildWidget(self, pos):
        return self._layout.takeAt(pos).widget()

    def addChildWidget(self, w):
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

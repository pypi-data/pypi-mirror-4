# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

import sys

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.editor import *

class ValueButton(QtGui.QPushButton, BaseWidget, EnableLogic, ViewLogic, EditLogic):
    __metaclass__ = QWallabyMeta

    value = Meta.property("int")

    def __init__(self, *args):
        QtGui.QPushButton.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QPushButton, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self._setValue)
        EditLogic.__init__(self, Editor, self._getValue)

        self.released.connect(self._released)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setCheckable(True)

        self._labelsSingleViewer = None

    def _setValue(self, value):
        self.setChecked(value == self.value)

    def _getValue(self):
        return self.value

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)

        if self._labelsSingleViewer: self._labelsSingleViewer.destroy()
        self._labelsSingleViewer = None

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self, raw=True)
        EditLogic.register(self)

        if self.path: self._labelsSingleViewer = Viewer(self.room, self._setLabels, self.path+"Labels", raw=True)

    def _setLabels(self, labels):
        if labels and len(labels) > self.value:
            self.setText(labels[self.value])

    def _released(self):
        if not self.isChecked():
            self.setChecked(True)
        else:
            if self._editor: self._editor._fieldChanged()

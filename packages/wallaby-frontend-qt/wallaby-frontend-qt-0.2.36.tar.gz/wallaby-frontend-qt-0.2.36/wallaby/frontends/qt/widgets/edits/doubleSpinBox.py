# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

import sys

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.doubleViewer import *
from wallaby.pf.peer.doubleEditor import *

class DoubleSpinBox(QtGui.QDoubleSpinBox, BaseWidget, EnableLogic, ViewLogic, EditLogic, TriggeredPillowsLogic):
    __metaclass__ = QWallabyMeta

    throwWhileEditing = Meta.property("bool", extended=True, default=True)
    triggers = Meta.property("list", readOnly=True, default=["", "changed"])

    def __init__(self, *args):
        QtGui.QDoubleSpinBox.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QDoubleSpinBox, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, DoubleViewer, self._setValue)
        EditLogic.__init__(self, DoubleEditor, self.value)
        TriggeredPillowsLogic.__init__(self)

        self._changed = True

        self._readOnly = self.isReadOnly()
        self.valueChanged.connect(self._spin)

    def _setEnabled(self, enabled):
        if self._readOnly: return

        if self.hideIfDisabled:
            self.setVisible(enabled)
        else:
            self.setReadOnly(not enabled)

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)
        TriggeredPillowsLogic.deregister(self, remove)

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)
        EditLogic.register(self)
        TriggeredPillowsLogic.register(self)

    def _resolve(self, value, **ka):
        if value==None:
            self._setValue(0.0)
        else:
            self._setValue(value)

        if self._editor: self._editor._resolve(**ka)

    def _value(self):
        val = self.value()
        if self.decimals() == 0:
            return int(val)
        else:
            return val

    def _spin(self, val):
        self.trigger("changed")
        if self._editor and self._changed:
            self._editor._fieldChanged()

    def _setValue(self, value):
        self._changed = False
        if isinstance(value, basestring): value = float(value)
        self.setValue(value)
        self._changed = True


# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *
import sys

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.dateViewer import *
from wallaby.pf.peer.dateEditor import *

class DateEdit(QtGui.QDateEdit, BaseWidget, EnableLogic, ViewLogic, EditLogic):
    __metaclass__ = QWallabyMeta

    defaultToNow = Meta.property("bool", extended=True)

    def __init__(self, *args):
        QtGui.QDateEdit.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QDateEdit, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, DateViewer, self._setValue)
        EditLogic.__init__(self, DateEditor, self._value)

        self._changed = True

        self._readOnly = self.isReadOnly()
        self.dateChanged.connect(self._valueChanged)

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

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)
        EditLogic.register(self)

        if self.defaultToNow:
            d = QtCore.QDate.currentDate()
        else:
            d = QtCore.QDate(1900, 1, 1)
 

    def _resolve(self, value, **ka):
        self._setValue(value)
        if self._editor: self._editor._resolve(**ka)

    def _value(self):
        d = self.date()

        return [d.year(), d.month(), d.day()]

    def _valueChanged(self, val):
        if self._editor and self._changed:
            self._editor._fieldChanged()

    def _setValue(self, value):
        if value == None:
            if self.defaultToNow:
                d = QtCore.QDate.currentDate()
            else:
                d = QtCore.QDate(1900, 1, 1)
        else:
            if len(value) >= 3:
                d = QtCore.QDate(value[0], value[1], value[2])
            
        self._changed = False
        self.setDate(d)
        self._changed = True


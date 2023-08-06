# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *
import sys

from ..baseWidget import *
from ..logics import *
from UI_numericLineEdit import *

from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.editor import *

class NumericLineEdit(QtGui.QWidget, Ui_NumericLineEdit, BaseWidget, EnableLogic, ViewLogic, EditLogic):
    __metaclass__ = QWallabyMeta

    labelText    = Meta.property("string")
    unit         = Meta.property("string")
    hasSetButton = Meta.property("bool")
    decimals     = Meta.property("int")
    minimum      = Meta.property("double")
    maximum      = Meta.property("double")
    singleStep   = Meta.property("double")

    def __del__(self):
        print "DESTRUCT NUMERICLINEEDIT"

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QWidget, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self.setValue)
        EditLogic.__init__(self, Editor, self.getValue)

        self._ignorePalette = True

        self.setupUi(self)

        self._value = 0

        self.doubleSpinBox.editingFinished.connect(self.editingFinishedCB)
        self.pushButtonSet.clicked.connect(self.editingFinishedCB)

        self.registerPalette()

    def editingFinishedCB(self, *args):
        if self._editor:
            self._editor._fieldChanged()

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self, raw=True)
        EditLogic.register(self, selectCallback=self._select)

        if self.decimals is not None: self.doubleSpinBox.setDecimals(self.decimals)
        if self.minimum is not None: self.doubleSpinBox.setMinimum(self.minimum)
        if self.maximum is not None: self.doubleSpinBox.setMaximum(self.maximum)
        if self.singleStep is not None: self.doubleSpinBox.setSingleStep(self.singleStep)

        if self.labelText and self.labelText != '':
            self.nameLabel.show()
            self.nameLabel.setText(self.labelText)
        else:
            self.nameLabel.hide()

        if self.unit and self.unit != '':
            self.unitLabel.show()
            self.unitLabel.setText(self.unit)
        else:
            self.unitLabel.hide()
        
        if self.hasSetButton:
            self.pushButtonSet.show()
        else:
            self.pushButtonSet.hide()
 
    def getValue(self):
        return self.doubleSpinBox.value()

    def _setFloat(self, value, cb):
        try:
            floatValue = float(value)
            if floatValue == None: floatValue = 0.0
            cb(floatValue)
        except:
            cb(0.0)

    def setValue(self, value):
        self._value = value
        self._setFloat(value, self.doubleSpinBox.setValue)

    def setMaxValue(self, value):
        self._setFloat(value, self.doubleSpinBox.setMaximum)
        self._setFloat(self._value, self.doubleSpinBox.setValue)

    def setMinValue(self, value):
        self._setFloat(value, self.doubleSpinBox.setMinimum)
        self._setFloat(self._value, self.doubleSpinBox.setValue)

    def setSingleStepValue(self, value):
        self._setFloat(value, self.doubleSpinBox.setSingleStep)
        self._setFloat(self._value, self.doubleSpinBox.setValue)
        
    def _select(self):
        self.doubleSpinBox.setFocus()
    
    def childPalette(self):
        return self.doubleSpinBox.palette()
    
    def setChildPalette(self, p):
        self.doubleSpinBox.setPalette(p)

# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..logics import *
from ..baseWidget import *

from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.editor import *

class Slider(QtGui.QSlider, BaseWidget, EnableLogic, ViewLogic, EditLogic):
    __metaclass__ = QWallabyMeta

    min = Meta.property("int")
    max = Meta.property("int")

    def __init__(self, *args):
        QtGui.QSlider.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QSlider, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self.setVal)
        EditLogic.__init__(self, Editor, self.sliderPosition)

        self.valueChanged.connect(self.changedValue)
        self._pause = False

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self, raw=True)
        EditLogic.register(self)

        if self.min: self.setMinimum(self.min)
        if self.max: self.setMaximum(self.max)

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)

    def setVal(self, value):
        try:
            valueInt = int(value)
        except:
            valueInt = 0

        self._pause = True
        self.setValue(valueInt)
        self._pause = False

    def changedValue(self):
        if self._editor and not self._pause: self._editor._fieldChanged()

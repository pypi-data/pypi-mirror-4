# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.viewer import *

class Progress(QtGui.QProgressBar, BaseWidget, EnableLogic, ViewLogic):
    __metaclass__ = QWallabyMeta

    min = Meta.property("int")
    max = Meta.property("int")

    def __init__(self, *args):
        QtGui.QProgressBar.__init__(self, *args)
        BaseWidget.__init__(self, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self._setText)

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)

        if self.min: self.setMinimum(self.min)
        if self.max: self.setMaximum(self.max)

    def _setText(self, text):
        try:
            i = int(text)
        except ValueError:
            i = 0

        self.setValue(i)

    def conflict(self, doc):
        pass

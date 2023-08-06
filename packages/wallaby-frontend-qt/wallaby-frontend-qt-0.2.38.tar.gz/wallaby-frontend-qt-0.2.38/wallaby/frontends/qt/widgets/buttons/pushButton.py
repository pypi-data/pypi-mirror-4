# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

import sys

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.booleanViewer import *
from wallaby.pf.peer.booleanEditor import *

class PushButton(QtGui.QPushButton, BaseWidget, EnableLogic, ViewLogic, EditLogic, TriggeredPillowsLogic):
    __metaclass__ = QWallabyMeta

    def __init__(self, *args):
        QtGui.QPushButton.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QPushButton, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, BooleanViewer, self.setChecked)
        EditLogic.__init__(self, BooleanEditor, self.isChecked)

        self.released.connect(self._released)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)
        EditLogic.register(self)

    def _released(self):
        if self._editor: self._editor._fieldChanged()
 

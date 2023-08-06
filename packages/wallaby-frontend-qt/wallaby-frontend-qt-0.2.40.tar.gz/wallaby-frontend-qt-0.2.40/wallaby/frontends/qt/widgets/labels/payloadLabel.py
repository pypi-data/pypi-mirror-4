# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..baseWidget import *

from wallaby.pf.peer.payloadCallback import *

class PayloadLabel(QtGui.QLabel, BaseWidget):
    __metaclass__ = QWallabyMeta

    room   = Meta.property("string")
    pillow = Meta.property("string")

    def __init__(self, *args):
        QtGui.QLabel.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QLabel, *args)

        self._peer = None

    def deregister(self, remove=False):
        if self._peer: self._peer.destroy(remove)
        self._peer = None

    def register(self):
        self._peer = PayloadCallback(self.room, self.pillow, self.setText)


# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

import sys
from wallaby.common.sets import OrderedSet

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.actionButtonPeer import *

class ActionButton(QtGui.QPushButton, BaseWidget, EnableLogic, TriggeredPillowsLogic):
    __metaclass__ = QWallabyMeta

    room     = Meta.property("string")
    pillow   = Meta.property("string")
    feathers = Meta.property("string")
    tab      = Meta.property("string")

    triggers = Meta.property("list", readOnly=True, default=["", "clicked", "pressed", "released"])

    def __init__(self, *args):
        QtGui.QPushButton.__init__(self, *args)

        BaseWidget.__init__(self, QtGui.QPushButton, *args)
        EnableLogic.__init__(self)
        TriggeredPillowsLogic.__init__(self)

        self._peer = None

        self.setEnabled(True)
        self.clicked.connect(self.buttonClicked)

        from functools import partial
        self.clicked.connect(partial(self.trigger, "clicked", None))
        self.pressed.connect(partial(self.trigger, "pressed"))
        self.released.connect(partial(self.trigger, "released"))

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def overlayLabel(self):
        rooms = OrderedSet()
        rooms[self.room] = True

        if self.pillow != None:
            rooms |= House.pillowRooms(self.room, self.pillow, self.feathers)

        if len(rooms) == 0:
            rooms.add(None)

        label = []
        label.append(rooms)
        if self.pillow != None:
            label.append(self.pillow)

        return label

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        TriggeredPillowsLogic.deregister(self, remove)

        if self._peer: self._peer.destroy(remove)
        self._peer = None

    def register(self):
        EnableLogic.register(self)
        TriggeredPillowsLogic.register(self)

        if self.pillow:
            self._peer = ActionButtonPeer(self.room, self.pillow, self.feathers, tab=self.tab, otherPillows=None)

    def buttonClicked(self):
        if self._peer: self._peer.buttonClicked()
        

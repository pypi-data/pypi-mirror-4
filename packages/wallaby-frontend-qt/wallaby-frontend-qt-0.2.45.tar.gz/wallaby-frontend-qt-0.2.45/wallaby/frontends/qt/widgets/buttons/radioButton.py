# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *
import sys

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.editor import *

class RadioButton(QtGui.QRadioButton, BaseWidget, EnableLogic, ViewLogic, EditLogic, TriggeredPillowsLogic):
    __metaclass__ = QWallabyMeta

    value = Meta.property("string")

    triggers = Meta.property("list", default=["","clicked", "pressed", "released", "checked", "unchecked"])

    def __init__(self, *args):
        QtGui.QRadioButton.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QCheckBox, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self.viewCallback)
        EditLogic.__init__(self, Editor, self.editCallback)
        TriggeredPillowsLogic.__init__(self)

        self.clicked.connect(self._clicked)

        from functools import partial
        self.clicked.connect(partial(self.trigger, "clicked", None)) # ignore argument
        self.pressed.connect(partial(self.trigger, "pressed"))
        self.released.connect(partial(self.trigger, "released"))

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)
        TriggeredPillowsLogic.deregister(self, remove)

    def _clicked(self, checked):
        if checked:
            self.trigger("checked") 
            if self._editor: self._editor._fieldChanged()
        else:
            self.trigger("unchecked") 

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)
        EditLogic.register(self)
        TriggeredPillowsLogic.register(self)

    def _resolve(self, value, **ka):
        self.viewCallback(value)
        if self._editor: 
            self._editor._resolve(**ka)
            self._editor._fieldChanged()

    def viewCallback(self, value):
        if self.path and value == self.value: 
            self.trigger("checked") 
            self.setChecked(True)

    def editCallback(self):
        return self.value

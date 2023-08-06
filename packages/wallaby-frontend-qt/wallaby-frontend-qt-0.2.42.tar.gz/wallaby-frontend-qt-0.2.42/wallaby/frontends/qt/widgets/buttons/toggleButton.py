# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from wallaby.frontends.qt.widgets.buttons.pushButton import PushButton
from ..logics import *

class ToggleButton(PushButton):
    __metaclass__ = QWallabyMeta

    def __init__(self, *args):
        PushButton.__init__(self, *args)
        self.setCheckable(True)

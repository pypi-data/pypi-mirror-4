#!/usr/bin/env python
# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.


import wallaby.FXUI as FXUI

from wallaby.qt_combat import *

from UI_loginDialog import Ui_LoginDialog

class LoginDialog(QtGui.QDialog, Ui_LoginDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        # set up User Interface (widgets, layout...)
        self.setupUi(self)

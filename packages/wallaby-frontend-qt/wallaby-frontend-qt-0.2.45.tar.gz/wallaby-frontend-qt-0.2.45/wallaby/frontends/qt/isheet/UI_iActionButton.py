# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/iActionButton.ui'
#
# Created: Fri Dec 28 14:05:17 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_IActionButton(object):
    def setupUi(self, IActionButton):
        IActionButton.setObjectName(_fromUtf8("IActionButton"))
        IActionButton.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(IActionButton)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = GroupBox(IActionButton)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_4 = GroupBox(IActionButton)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.verticalLayout.addWidget(self.groupBox_4)
        self.groupBox_2 = GroupBox(IActionButton)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout.addWidget(self.groupBox_2)
        spacerItem = QtGui.QSpacerItem(20, 172, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(IActionButton)
        QtCore.QMetaObject.connectSlotsByName(IActionButton)

    def retranslateUi(self, IActionButton):
        IActionButton.setWindowTitle(QtGui.QApplication.translate("IActionButton", "ActionButton preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("IActionButton", "Basic settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setProperty("template", QtGui.QApplication.translate("IActionButton", "inspector-groupbox-room", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("IActionButton", "Triggered pillows", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setProperty("template", QtGui.QApplication.translate("IActionButton", "inspector-groupbox-triggeredpillows", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("IActionButton", "Enable logic", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setProperty("template", QtGui.QApplication.translate("IActionButton", "inspector-groupbox-enablelogic", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.containers.groupBox import GroupBox

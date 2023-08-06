# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/iLabel.ui'
#
# Created: Sun Dec 16 18:13:20 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ILabel(object):
    def setupUi(self, ILabel):
        ILabel.setObjectName(_fromUtf8("ILabel"))
        ILabel.resize(446, 169)
        self.verticalLayout = QtGui.QVBoxLayout(ILabel)
        self.verticalLayout.setMargin(12)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = GroupBox(ILabel)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = GroupBox(ILabel)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout.addWidget(self.groupBox_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(ILabel)
        QtCore.QMetaObject.connectSlotsByName(ILabel)

    def retranslateUi(self, ILabel):
        ILabel.setWindowTitle(QtGui.QApplication.translate("ILabel", "Label preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ILabel", "Basic Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setProperty("template", QtGui.QApplication.translate("ILabel", "inspector-groupbox-roomandpath", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("ILabel", "Enable logic", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setProperty("template", QtGui.QApplication.translate("ILabel", "inspector-groupbox-enablelogic", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.containers.groupBox import GroupBox

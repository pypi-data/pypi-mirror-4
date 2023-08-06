# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/iStacked.ui'
#
# Created: Sun Dec 16 18:13:23 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_2 = GroupBox(Form)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox = GroupBox(Form)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_3 = GroupBox(Form)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout.addWidget(self.groupBox_3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Form", "Basic settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setProperty("template", QtGui.QApplication.translate("Form", "inspector-groupbox-room", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Sheets", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setProperty("template", QtGui.QApplication.translate("Form", "inspector-container-sheets", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Form", "Multipage settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setProperty("template", QtGui.QApplication.translate("Form", "inspector-groupbox-multipage", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.containers.groupBox import GroupBox

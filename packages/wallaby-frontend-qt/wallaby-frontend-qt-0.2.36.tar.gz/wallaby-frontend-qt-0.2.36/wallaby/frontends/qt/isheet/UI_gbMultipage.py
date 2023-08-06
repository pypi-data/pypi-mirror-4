# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './wallaby/frontends/qt/isheet/gbMultipage.ui'
#
# Created: Mon Dec  3 18:07:06 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_CRoom(object):
    def setupUi(self, CRoom):
        CRoom.setObjectName(_fromUtf8("CRoom"))
        CRoom.resize(469, 158)
        self.verticalLayout = QtGui.QVBoxLayout(CRoom)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(CRoom)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.LineEdit = LineEdit(CRoom)
        self.LineEdit.setObjectName(_fromUtf8("LineEdit"))
        self.verticalLayout.addWidget(self.LineEdit)
        self.label_2 = QtGui.QLabel(CRoom)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.LineEdit_2 = LineEdit(CRoom)
        self.LineEdit_2.setObjectName(_fromUtf8("LineEdit_2"))
        self.verticalLayout.addWidget(self.LineEdit_2)

        self.retranslateUi(CRoom)
        QtCore.QMetaObject.connectSlotsByName(CRoom)

    def retranslateUi(self, CRoom):
        CRoom.setWindowTitle(QtGui.QApplication.translate("CRoom", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CRoom", "Container\'s identifier", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit.setProperty("template", QtGui.QApplication.translate("CRoom", "inspector-identifier", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("CRoom", "Default sheet name", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_2.setProperty("template", QtGui.QApplication.translate("CRoom", "inspector-defaultsheet", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.edits.lineEdit import LineEdit

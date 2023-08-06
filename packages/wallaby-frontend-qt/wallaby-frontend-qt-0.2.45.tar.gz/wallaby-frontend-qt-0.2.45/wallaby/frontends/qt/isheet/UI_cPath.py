# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './wallaby/frontends/qt/isheet/cPath.ui'
#
# Created: Sun Dec  2 13:03:07 2012
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
        CRoom.resize(522, 70)
        self.verticalLayout = QtGui.QVBoxLayout(CRoom)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(CRoom)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.LineEdit = LineEdit(CRoom)
        self.LineEdit.setObjectName(_fromUtf8("LineEdit"))
        self.verticalLayout.addWidget(self.LineEdit)

        self.retranslateUi(CRoom)
        QtCore.QMetaObject.connectSlotsByName(CRoom)

    def retranslateUi(self, CRoom):
        CRoom.setWindowTitle(QtGui.QApplication.translate("CRoom", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CRoom", "<html><head/><body><p>The widgets\'s path. The path is the dot-separated key-list in the document.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit.setProperty("template", QtGui.QApplication.translate("CRoom", "inspector-path", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.edits.lineEdit import LineEdit

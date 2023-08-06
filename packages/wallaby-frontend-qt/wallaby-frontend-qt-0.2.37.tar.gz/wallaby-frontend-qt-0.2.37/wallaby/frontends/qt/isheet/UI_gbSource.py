# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './wallaby/frontends/qt/isheet/gbSource.ui'
#
# Created: Thu Dec  6 17:58:41 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_GbRoomAndPath(object):
    def setupUi(self, GbRoomAndPath):
        GbRoomAndPath.setObjectName(_fromUtf8("GbRoomAndPath"))
        GbRoomAndPath.resize(652, 89)
        self.gridLayout = QtGui.QGridLayout(GbRoomAndPath)
        self.gridLayout.setContentsMargins(0, 20, 0, 0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(GbRoomAndPath)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(GbRoomAndPath)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.LineEdit = LineEdit(GbRoomAndPath)
        self.LineEdit.setObjectName(_fromUtf8("LineEdit"))
        self.gridLayout.addWidget(self.LineEdit, 0, 1, 1, 1)
        self.LineEdit_2 = LineEdit(GbRoomAndPath)
        self.LineEdit_2.setObjectName(_fromUtf8("LineEdit_2"))
        self.gridLayout.addWidget(self.LineEdit_2, 2, 1, 1, 1)

        self.retranslateUi(GbRoomAndPath)
        QtCore.QMetaObject.connectSlotsByName(GbRoomAndPath)

    def retranslateUi(self, GbRoomAndPath):
        GbRoomAndPath.setWindowTitle(QtGui.QApplication.translate("GbRoomAndPath", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("GbRoomAndPath", "Document-id of source document", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "Path to data (list of strings)", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-source", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-sourcepath", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.edits.lineEdit import LineEdit

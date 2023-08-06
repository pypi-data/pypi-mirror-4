# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/gbQuery.ui'
#
# Created: Sun Dec 16 18:08:31 2012
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
        GbRoomAndPath.resize(652, 445)
        self.verticalLayout = QtGui.QVBoxLayout(GbRoomAndPath)
        self.verticalLayout.setContentsMargins(0, 20, 0, 0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.checkBox_3 = CheckBox(GbRoomAndPath)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.verticalLayout.addWidget(self.checkBox_3)
        self.groupBox_2 = QtGui.QGroupBox(GbRoomAndPath)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.LineEdit = LineEdit(self.groupBox_2)
        self.LineEdit.setObjectName(_fromUtf8("LineEdit"))
        self.gridLayout.addWidget(self.LineEdit, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.LineEdit_2 = LineEdit(self.groupBox_2)
        self.LineEdit_2.setObjectName(_fromUtf8("LineEdit_2"))
        self.gridLayout.addWidget(self.LineEdit_2, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.LineEdit_3 = LineEdit(self.groupBox_2)
        self.LineEdit_3.setObjectName(_fromUtf8("LineEdit_3"))
        self.gridLayout.addWidget(self.LineEdit_3, 3, 1, 1, 1)
        self.checkBox_2 = CheckBox(self.groupBox_2)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.gridLayout.addWidget(self.checkBox_2, 0, 0, 1, 2)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox = QtGui.QGroupBox(GbRoomAndPath)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.embeddedViewTable = EmbeddedViewTable(self.groupBox)
        self.embeddedViewTable.setMinimumSize(QtCore.QSize(0, 150))
        self.embeddedViewTable.setObjectName(_fromUtf8("embeddedViewTable"))
        self.verticalLayout_2.addWidget(self.embeddedViewTable)
        self.widget = QtGui.QWidget(self.groupBox)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.actionButton_2 = ActionButton(self.widget)
        self.actionButton_2.setObjectName(_fromUtf8("actionButton_2"))
        self.horizontalLayout.addWidget(self.actionButton_2)
        self.actionButton = ActionButton(self.widget)
        self.actionButton.setObjectName(_fromUtf8("actionButton"))
        self.horizontalLayout.addWidget(self.actionButton)
        self.verticalLayout_2.addWidget(self.widget)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(GbRoomAndPath)
        QtCore.QMetaObject.connectSlotsByName(GbRoomAndPath)

    def retranslateUi(self, GbRoomAndPath):
        GbRoomAndPath.setWindowTitle(QtGui.QApplication.translate("GbRoomAndPath", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_3.setText(QtGui.QApplication.translate("GbRoomAndPath", "Fill combobox with values from view", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_3.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-isview", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("GbRoomAndPath", "General Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-view", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("GbRoomAndPath", "View", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-viewpath", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("GbRoomAndPath", "Path of displayed value", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "Path of raw value", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_3.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-viewdisplaypath", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "Use the view\'s values as data (data must not be loaded by document-id)", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-dataview", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("GbRoomAndPath", "View arguments", None, QtGui.QApplication.UnicodeUTF8))
        self.embeddedViewTable.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-table-viewargs", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-viewargs-add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setText(QtGui.QApplication.translate("GbRoomAndPath", "remove", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-viewargs-remove", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.buttons.checkBox import CheckBox
from wallaby.frontends.qt.widgets.multi.embeddedViewTable import EmbeddedViewTable
from wallaby.frontends.qt.widgets.edits.lineEdit import LineEdit
from wallaby.frontends.qt.widgets.buttons.actionButton import ActionButton

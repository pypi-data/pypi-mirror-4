# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './wallaby/frontends/qt/isheet/gbTableSettings.ui'
#
# Created: Sun Dec 30 14:06:25 2012
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
        GbRoomAndPath.resize(654, 715)
        GbRoomAndPath.setMaximumSize(QtCore.QSize(16777215, 740))
        self.verticalLayout = QtGui.QVBoxLayout(GbRoomAndPath)
        self.verticalLayout.setContentsMargins(0, 20, 0, 0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.checkBox = CheckBox(GbRoomAndPath)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout.addWidget(self.checkBox)
        self.checkBox_2 = CheckBox(GbRoomAndPath)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.verticalLayout.addWidget(self.checkBox_2)
        self.checkBox_3 = CheckBox(GbRoomAndPath)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.verticalLayout.addWidget(self.checkBox_3)
        self.groupBox_2 = QtGui.QGroupBox(GbRoomAndPath)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.numericLineEdit = NumericLineEdit(self.groupBox_2)
        self.numericLineEdit.setObjectName(_fromUtf8("numericLineEdit"))
        self.gridLayout.addWidget(self.numericLineEdit, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.numericLineEdit_2 = NumericLineEdit(self.groupBox_2)
        self.numericLineEdit_2.setObjectName(_fromUtf8("numericLineEdit_2"))
        self.gridLayout.addWidget(self.numericLineEdit_2, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(GbRoomAndPath)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.embeddedViewTable_2 = EmbeddedViewTable(self.groupBox_3)
        self.embeddedViewTable_2.setMinimumSize(QtCore.QSize(0, 150))
        self.embeddedViewTable_2.setObjectName(_fromUtf8("embeddedViewTable_2"))
        self.verticalLayout_3.addWidget(self.embeddedViewTable_2)
        self.widget_2 = QtGui.QWidget(self.groupBox_3)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.actionButton_3 = ActionButton(self.widget_2)
        self.actionButton_3.setObjectName(_fromUtf8("actionButton_3"))
        self.horizontalLayout_2.addWidget(self.actionButton_3)
        self.actionButton_4 = ActionButton(self.widget_2)
        self.actionButton_4.setObjectName(_fromUtf8("actionButton_4"))
        self.horizontalLayout_2.addWidget(self.actionButton_4)
        self.verticalLayout_3.addWidget(self.widget_2)
        self.verticalLayout.addWidget(self.groupBox_3)
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
        self.checkBox.setText(QtGui.QApplication.translate("GbRoomAndPath", "The displayed content is a list (not a dict)", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-islist", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "Auto-resize cells", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-autoresize", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_3.setText(QtGui.QApplication.translate("GbRoomAndPath", "Display dict-content as list", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_3.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-aslist", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("GbRoomAndPath", "Minimum size of", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("GbRoomAndPath", "Columns", None, QtGui.QApplication.UnicodeUTF8))
        self.numericLineEdit.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-min-width", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "Rows", None, QtGui.QApplication.UnicodeUTF8))
        self.numericLineEdit_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-min-height", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("GbRoomAndPath", "Size hints", None, QtGui.QApplication.UnicodeUTF8))
        self.embeddedViewTable_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-table-sizehints", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_3.setText(QtGui.QApplication.translate("GbRoomAndPath", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_3.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-sizehints-add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_4.setText(QtGui.QApplication.translate("GbRoomAndPath", "remove", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_4.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-sizehints-remove", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("GbRoomAndPath", "Columns", None, QtGui.QApplication.UnicodeUTF8))
        self.embeddedViewTable.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-table-config", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-dbcolumns-add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setText(QtGui.QApplication.translate("GbRoomAndPath", "remove", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-dbcolumns-remove", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.buttons.checkBox import CheckBox
from wallaby.frontends.qt.widgets.multi.embeddedViewTable import EmbeddedViewTable
from wallaby.frontends.qt.widgets.buttons.actionButton import ActionButton
from wallaby.frontends.qt.widgets.edits.numericLineEdit import NumericLineEdit

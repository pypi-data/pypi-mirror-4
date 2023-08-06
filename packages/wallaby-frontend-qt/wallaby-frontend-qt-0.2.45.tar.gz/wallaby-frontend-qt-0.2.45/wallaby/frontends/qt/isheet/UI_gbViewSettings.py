# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/gbViewSettings.ui'
#
# Created: Sun Dec 16 18:08:32 2012
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
        GbRoomAndPath.resize(627, 839)
        self.gridLayout = QtGui.QGridLayout(GbRoomAndPath)
        self.gridLayout.setContentsMargins(0, 20, 0, 0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox_2 = QtGui.QGroupBox(GbRoomAndPath)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.checkBox = CheckBox(self.groupBox_2)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout.addWidget(self.checkBox)
        self.checkBox_2 = CheckBox(self.groupBox_2)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.verticalLayout.addWidget(self.checkBox_2)
        self.checkBox_3 = CheckBox(self.groupBox_2)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.verticalLayout.addWidget(self.checkBox_3)
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.LineEdit = LineEdit(self.groupBox_2)
        self.LineEdit.setObjectName(_fromUtf8("LineEdit"))
        self.verticalLayout.addWidget(self.LineEdit)
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.LineEdit_4 = LineEdit(self.groupBox_2)
        self.LineEdit_4.setObjectName(_fromUtf8("LineEdit_4"))
        self.verticalLayout.addWidget(self.LineEdit_4)
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.LineEdit_2 = LineEdit(self.groupBox_2)
        self.LineEdit_2.setObjectName(_fromUtf8("LineEdit_2"))
        self.verticalLayout.addWidget(self.LineEdit_2)
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.LineEdit_3 = LineEdit(self.groupBox_2)
        self.LineEdit_3.setObjectName(_fromUtf8("LineEdit_3"))
        self.verticalLayout.addWidget(self.LineEdit_3)
        self.gridLayout.addWidget(self.groupBox_2, 0, 0, 1, 1)
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
        self.gridLayout.addWidget(self.groupBox, 2, 0, 1, 1)
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
        self.gridLayout.addWidget(self.groupBox_3, 3, 0, 1, 1)

        self.retranslateUi(GbRoomAndPath)
        QtCore.QMetaObject.connectSlotsByName(GbRoomAndPath)

    def retranslateUi(self, GbRoomAndPath):
        GbRoomAndPath.setWindowTitle(QtGui.QApplication.translate("GbRoomAndPath", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("GbRoomAndPath", "General settings", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("GbRoomAndPath", "The query contains data (not only IDs)", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-hasdata", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "Display the \'Id\'-column", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-showid", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_3.setText(QtGui.QApplication.translate("GbRoomAndPath", "Enable multi-select", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_3.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-multiselect", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("GbRoomAndPath", "The query\'s identifier. The identifier is also used as room for the query arguments document.", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-view-identifier", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("GbRoomAndPath", "The view\'s path", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_4.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-view", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "The document\'s id of the query document (for elasticsearch)", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-querydocid", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("GbRoomAndPath", "The path of a sortable field (needs to be a float value)", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_3.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-orderpath", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("GbRoomAndPath", "Query arguments", None, QtGui.QApplication.UnicodeUTF8))
        self.embeddedViewTable.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-table-viewargs", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-viewargs-add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setText(QtGui.QApplication.translate("GbRoomAndPath", "remove", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-viewargs-remove", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("GbRoomAndPath", "Sortable columns", None, QtGui.QApplication.UnicodeUTF8))
        self.embeddedViewTable_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-sortable", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_3.setText(QtGui.QApplication.translate("GbRoomAndPath", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_3.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-sortable-add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_4.setText(QtGui.QApplication.translate("GbRoomAndPath", "remove", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_4.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-sortable-remove", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.buttons.checkBox import CheckBox
from wallaby.frontends.qt.widgets.multi.embeddedViewTable import EmbeddedViewTable
from wallaby.frontends.qt.widgets.edits.lineEdit import LineEdit
from wallaby.frontends.qt.widgets.buttons.actionButton import ActionButton

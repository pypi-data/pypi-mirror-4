# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/gbTriggeredPillows.ui'
#
# Created: Fri Dec 28 12:01:13 2012
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
        GbRoomAndPath.resize(669, 437)
        GbRoomAndPath.setMinimumSize(QtCore.QSize(0, 437))
        GbRoomAndPath.setMaximumSize(QtCore.QSize(16777215, 504))
        self.verticalLayout = QtGui.QVBoxLayout(GbRoomAndPath)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.embeddedViewTable = EmbeddedViewTable(GbRoomAndPath)
        self.embeddedViewTable.setMinimumSize(QtCore.QSize(0, 150))
        self.embeddedViewTable.setObjectName(_fromUtf8("embeddedViewTable"))
        self.verticalLayout.addWidget(self.embeddedViewTable)
        self.widget = QtGui.QWidget(GbRoomAndPath)
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
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(GbRoomAndPath)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.gridLayout = QtGui.QGridLayout(self.widget_2)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(self.widget_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.ComboBox = ComboBox(self.widget_2)
        self.ComboBox.setObjectName(_fromUtf8("ComboBox"))
        self.gridLayout.addWidget(self.ComboBox, 0, 2, 1, 1)
        self.label = QtGui.QLabel(self.widget_2)
        self.label.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.widget_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.ComboBox_2 = ComboBox(self.widget_2)
        self.ComboBox_2.setEditable(True)
        self.ComboBox_2.setObjectName(_fromUtf8("ComboBox_2"))
        self.gridLayout.addWidget(self.ComboBox_2, 1, 2, 1, 1)
        self.checkBox = CheckBox(self.widget_2)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout.addWidget(self.checkBox, 2, 2, 1, 1)
        self.verticalLayout.addWidget(self.widget_2)
        self.plainTextEdit = PlainTextEdit(GbRoomAndPath)
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.verticalLayout.addWidget(self.plainTextEdit)

        self.retranslateUi(GbRoomAndPath)
        QtCore.QMetaObject.connectSlotsByName(GbRoomAndPath)

    def retranslateUi(self, GbRoomAndPath):
        GbRoomAndPath.setWindowTitle(QtGui.QApplication.translate("GbRoomAndPath", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.embeddedViewTable.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-table-triggeredpillows", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-triggeredpillows-add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setText(QtGui.QApplication.translate("GbRoomAndPath", "remove", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-triggeredpillows-remove", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("GbRoomAndPath", "Feathers:", None, QtGui.QApplication.UnicodeUTF8))
        self.ComboBox.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-triggers", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("GbRoomAndPath", "Trigger", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("GbRoomAndPath", "Pillow", None, QtGui.QApplication.UnicodeUTF8))
        self.ComboBox_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-cb-pillow", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("GbRoomAndPath", "Is JSON", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-cb-isjson", None, QtGui.QApplication.UnicodeUTF8))
        self.plainTextEdit.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-pe-feathers", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.buttons.checkBox import CheckBox
from wallaby.frontends.qt.widgets.multi.embeddedViewTable import EmbeddedViewTable
from wallaby.frontends.qt.widgets.combo.comboBox import ComboBox
from wallaby.frontends.qt.widgets.buttons.actionButton import ActionButton
from wallaby.frontends.qt.widgets.edits.plainTextEdit import PlainTextEdit

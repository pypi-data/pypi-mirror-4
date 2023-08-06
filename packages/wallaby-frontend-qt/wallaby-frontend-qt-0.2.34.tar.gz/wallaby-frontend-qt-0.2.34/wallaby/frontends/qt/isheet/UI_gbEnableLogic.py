# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/gbEnableLogic.ui'
#
# Created: Fri Dec 28 12:03:49 2012
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
        Form.resize(523, 403)
        Form.setMaximumSize(QtCore.QSize(16777215, 450))
        self.verticalLayout_2 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.checkBox = CheckBox(self.groupBox)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout.addWidget(self.checkBox)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.embeddedViewTable = EmbeddedViewTable(self.groupBox)
        self.embeddedViewTable.setMinimumSize(QtCore.QSize(0, 150))
        self.embeddedViewTable.setObjectName(_fromUtf8("embeddedViewTable"))
        self.verticalLayout.addWidget(self.embeddedViewTable)
        self.widget = QtGui.QWidget(self.groupBox)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.actionButton = ActionButton(self.widget)
        self.actionButton.setObjectName(_fromUtf8("actionButton"))
        self.horizontalLayout.addWidget(self.actionButton)
        self.actionButton_2 = ActionButton(self.widget)
        self.actionButton_2.setObjectName(_fromUtf8("actionButton_2"))
        self.horizontalLayout.addWidget(self.actionButton_2)
        self.verticalLayout.addWidget(self.widget)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(Form)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.LineEdit = LineEdit(self.groupBox_2)
        self.LineEdit.setObjectName(_fromUtf8("LineEdit"))
        self.gridLayout.addWidget(self.LineEdit, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.LineEdit_2 = LineEdit(self.groupBox_2)
        self.LineEdit_2.setObjectName(_fromUtf8("LineEdit_2"))
        self.gridLayout.addWidget(self.LineEdit_2, 1, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Payload-based enable triggers", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Form", "Hide the widget, when it is disabled", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setProperty("template", QtGui.QApplication.translate("Form", "inspector-hideIfDisabled", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Enable the widget if one of the following feathers is found in an enable pillow.", None, QtGui.QApplication.UnicodeUTF8))
        self.embeddedViewTable.setProperty("template", QtGui.QApplication.translate("Form", "inspector-enable-feathers", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setText(QtGui.QApplication.translate("Form", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton.setProperty("template", QtGui.QApplication.translate("Form", "inspector-enable-feathers-add", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setText(QtGui.QApplication.translate("Form", "remove", None, QtGui.QApplication.UnicodeUTF8))
        self.actionButton_2.setProperty("template", QtGui.QApplication.translate("Form", "inspector-enable-feathers-remove", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Form", "Document-based enable triggers", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Path to the enable value", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit.setProperty("template", QtGui.QApplication.translate("Form", "inspector-enable-path", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Enable value", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_2.setProperty("template", QtGui.QApplication.translate("Form", "inspector-enable-value", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.buttons.checkBox import CheckBox
from wallaby.frontends.qt.widgets.multi.embeddedViewTable import EmbeddedViewTable
from wallaby.frontends.qt.widgets.edits.lineEdit import LineEdit
from wallaby.frontends.qt.widgets.buttons.actionButton import ActionButton

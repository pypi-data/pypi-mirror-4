# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './wallaby/frontends/qt/isheet/gbPillowAndFeathers.ui'
#
# Created: Mon Dec  3 11:50:55 2012
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
        Form.resize(424, 126)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.widget = QtGui.QWidget(Form)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, -1, 0, -1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.LineEdit = LineEdit(self.widget)
        self.LineEdit.setObjectName(_fromUtf8("LineEdit"))
        self.gridLayout.addWidget(self.LineEdit, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.LineEdit_2 = LineEdit(self.widget)
        self.LineEdit_2.setObjectName(_fromUtf8("LineEdit_2"))
        self.gridLayout.addWidget(self.LineEdit_2, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Throw the following pillow with optional \"feathers\"", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Pillow", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit.setProperty("template", QtGui.QApplication.translate("Form", "inspector-pillow", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Feathers", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_2.setProperty("template", QtGui.QApplication.translate("Form", "inspector-feathers", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.edits.lineEdit import LineEdit

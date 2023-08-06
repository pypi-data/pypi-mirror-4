# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/iNumericLineEdit.ui'
#
# Created: Sun Dec 16 18:13:21 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ILineEdit(object):
    def setupUi(self, ILineEdit):
        ILineEdit.setObjectName(_fromUtf8("ILineEdit"))
        ILineEdit.resize(523, 488)
        self.verticalLayout = QtGui.QVBoxLayout(ILineEdit)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = GroupBox(ILineEdit)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_4 = QtGui.QGroupBox(ILineEdit)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.LineEdit = LineEdit(self.groupBox_4)
        self.LineEdit.setObjectName(_fromUtf8("LineEdit"))
        self.gridLayout.addWidget(self.LineEdit, 0, 2, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_4)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_4)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.LineEdit_2 = LineEdit(self.groupBox_4)
        self.LineEdit_2.setObjectName(_fromUtf8("LineEdit_2"))
        self.gridLayout.addWidget(self.LineEdit_2, 2, 2, 1, 1)
        self.numericLineEdit = NumericLineEdit(self.groupBox_4)
        self.numericLineEdit.setObjectName(_fromUtf8("numericLineEdit"))
        self.gridLayout.addWidget(self.numericLineEdit, 4, 0, 1, 3)
        self.checkBox = CheckBox(self.groupBox_4)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout.addWidget(self.checkBox, 3, 0, 1, 3)
        self.numericLineEdit_3 = NumericLineEdit(self.groupBox_4)
        self.numericLineEdit_3.setObjectName(_fromUtf8("numericLineEdit_3"))
        self.gridLayout.addWidget(self.numericLineEdit_3, 5, 0, 1, 3)
        self.numericLineEdit_2 = NumericLineEdit(self.groupBox_4)
        self.numericLineEdit_2.setObjectName(_fromUtf8("numericLineEdit_2"))
        self.gridLayout.addWidget(self.numericLineEdit_2, 6, 0, 1, 3)
        self.numericLineEdit_4 = NumericLineEdit(self.groupBox_4)
        self.numericLineEdit_4.setObjectName(_fromUtf8("numericLineEdit_4"))
        self.gridLayout.addWidget(self.numericLineEdit_4, 7, 0, 1, 3)
        self.verticalLayout.addWidget(self.groupBox_4)
        self.groupBox_3 = GroupBox(ILineEdit)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox_2 = GroupBox(ILineEdit)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout.addWidget(self.groupBox_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(ILineEdit)
        QtCore.QMetaObject.connectSlotsByName(ILineEdit)

    def retranslateUi(self, ILineEdit):
        ILineEdit.setWindowTitle(QtGui.QApplication.translate("ILineEdit", "LineEdit preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ILineEdit", "Basic settings", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-groupbox-roomandpath", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("ILineEdit", "Numeric lineedit settings", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-label", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ILineEdit", "Label", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ILineEdit", "Unit", None, QtGui.QApplication.UnicodeUTF8))
        self.LineEdit_2.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-unit", None, QtGui.QApplication.UnicodeUTF8))
        self.numericLineEdit.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-decimals", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("ILineEdit", "Show \"set\" button", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-setbutton", None, QtGui.QApplication.UnicodeUTF8))
        self.numericLineEdit_3.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-minimum", None, QtGui.QApplication.UnicodeUTF8))
        self.numericLineEdit_2.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-maximum", None, QtGui.QApplication.UnicodeUTF8))
        self.numericLineEdit_4.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-singlestep", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("ILineEdit", "Triggered pillows", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-groupbox-triggeredpillows", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("ILineEdit", "Enable logic", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-groupbox-enablelogic", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.buttons.checkBox import CheckBox
from wallaby.frontends.qt.widgets.edits.lineEdit import LineEdit
from wallaby.frontends.qt.widgets.containers.groupBox import GroupBox
from wallaby.frontends.qt.widgets.edits.numericLineEdit import NumericLineEdit

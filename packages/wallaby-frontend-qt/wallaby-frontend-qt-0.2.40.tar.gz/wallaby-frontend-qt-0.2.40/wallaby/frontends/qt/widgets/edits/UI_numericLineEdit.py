# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/widgets/edits/numericLineEdit.ui'
#
# Created: Mon Nov 19 14:07:43 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_NumericLineEdit(object):
    def setupUi(self, NumericLineEdit):
        NumericLineEdit.setObjectName(_fromUtf8("NumericLineEdit"))
        NumericLineEdit.resize(220, 37)
        self.horizontalLayout = QtGui.QHBoxLayout(NumericLineEdit)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setMargin(1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.nameLabel = QtGui.QLabel(NumericLineEdit)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nameLabel.sizePolicy().hasHeightForWidth())
        self.nameLabel.setSizePolicy(sizePolicy)
        self.nameLabel.setMinimumSize(QtCore.QSize(50, 0))
        self.nameLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.nameLabel.setIndent(2)
        self.nameLabel.setObjectName(_fromUtf8("nameLabel"))
        self.horizontalLayout.addWidget(self.nameLabel)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(NumericLineEdit)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox.setSizePolicy(sizePolicy)
        self.doubleSpinBox.setMinimumSize(QtCore.QSize(100, 0))
        self.doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox.setReadOnly(False)
        self.doubleSpinBox.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.doubleSpinBox.setAccelerated(False)
        self.doubleSpinBox.setPrefix(_fromUtf8(""))
        self.doubleSpinBox.setSuffix(_fromUtf8(""))
        self.doubleSpinBox.setMaximum(99999.99)
        self.doubleSpinBox.setProperty("value", 99999.99)
        self.doubleSpinBox.setObjectName(_fromUtf8("doubleSpinBox"))
        self.horizontalLayout.addWidget(self.doubleSpinBox)
        self.unitLabel = QtGui.QLabel(NumericLineEdit)
        self.unitLabel.setMinimumSize(QtCore.QSize(30, 0))
        self.unitLabel.setMaximumSize(QtCore.QSize(30, 16777215))
        self.unitLabel.setObjectName(_fromUtf8("unitLabel"))
        self.horizontalLayout.addWidget(self.unitLabel)
        self.pushButtonSet = QtGui.QPushButton(NumericLineEdit)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonSet.sizePolicy().hasHeightForWidth())
        self.pushButtonSet.setSizePolicy(sizePolicy)
        self.pushButtonSet.setMaximumSize(QtCore.QSize(30, 16777215))
        self.pushButtonSet.setBaseSize(QtCore.QSize(0, 0))
        self.pushButtonSet.setObjectName(_fromUtf8("pushButtonSet"))
        self.horizontalLayout.addWidget(self.pushButtonSet)

        self.retranslateUi(NumericLineEdit)
        QtCore.QMetaObject.connectSlotsByName(NumericLineEdit)

    def retranslateUi(self, NumericLineEdit):
        NumericLineEdit.setWindowTitle(QtGui.QApplication.translate("NumericLineEdit", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.nameLabel.setText(QtGui.QApplication.translate("NumericLineEdit", "X", None, QtGui.QApplication.UnicodeUTF8))
        self.unitLabel.setText(QtGui.QApplication.translate("NumericLineEdit", "nm", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonSet.setText(QtGui.QApplication.translate("NumericLineEdit", "Set", None, QtGui.QApplication.UnicodeUTF8))


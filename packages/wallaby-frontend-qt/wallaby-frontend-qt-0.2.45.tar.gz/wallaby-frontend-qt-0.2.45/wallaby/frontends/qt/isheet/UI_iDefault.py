# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/iDefault.ui'
#
# Created: Tue Nov 27 12:58:17 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_IDefault(object):
    def setupUi(self, IDefault):
        IDefault.setObjectName(_fromUtf8("IDefault"))
        IDefault.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(IDefault)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(IDefault)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(IDefault)
        QtCore.QMetaObject.connectSlotsByName(IDefault)

    def retranslateUi(self, IDefault):
        IDefault.setWindowTitle(QtGui.QApplication.translate("IDefault", "Default Tab", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("IDefault", "Please select a widget.", None, QtGui.QApplication.UnicodeUTF8))


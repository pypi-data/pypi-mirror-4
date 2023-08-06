# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/loginDialog.ui'
#
# Created: Mon Nov 19 14:05:03 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName(_fromUtf8("LoginDialog"))
        LoginDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        LoginDialog.resize(390, 267)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LoginDialog.sizePolicy().hasHeightForWidth())
        LoginDialog.setSizePolicy(sizePolicy)
        LoginDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(LoginDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(LoginDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.userEdit = QtGui.QLineEdit(self.groupBox)
        self.userEdit.setGeometry(QtCore.QRect(170, 100, 161, 22))
        self.userEdit.setText(_fromUtf8(""))
        self.userEdit.setObjectName(_fromUtf8("userEdit"))
        self.pwdEdit = QtGui.QLineEdit(self.groupBox)
        self.pwdEdit.setGeometry(QtCore.QRect(170, 140, 161, 22))
        self.pwdEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.pwdEdit.setObjectName(_fromUtf8("pwdEdit"))
        self.image = QtGui.QLabel(self.groupBox)
        self.image.setGeometry(QtCore.QRect(20, 40, 131, 141))
        self.image.setText(_fromUtf8(""))
        self.image.setPixmap(QtGui.QPixmap(_fromUtf8(":/images/images/user_big.png")))
        self.image.setObjectName(_fromUtf8("image"))
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(LoginDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LoginDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LoginDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LoginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        LoginDialog.setWindowTitle(QtGui.QApplication.translate("LoginDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("LoginDialog", "Anmeldung", None, QtGui.QApplication.UnicodeUTF8))
        self.userEdit.setPlaceholderText(QtGui.QApplication.translate("LoginDialog", "Benutzername", None, QtGui.QApplication.UnicodeUTF8))
        self.pwdEdit.setPlaceholderText(QtGui.QApplication.translate("LoginDialog", "Passwort", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc

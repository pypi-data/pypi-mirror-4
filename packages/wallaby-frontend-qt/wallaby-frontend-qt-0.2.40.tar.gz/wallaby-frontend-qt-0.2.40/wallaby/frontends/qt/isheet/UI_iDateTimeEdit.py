# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './wallaby/frontends/qt/isheet/iDateTimeEdit.ui'
#
# Created: Mon Jan 21 08:50:31 2013
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
        ILineEdit.resize(406, 257)
        self.verticalLayout = QtGui.QVBoxLayout(ILineEdit)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = GroupBox(ILineEdit)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_4 = QtGui.QGroupBox(ILineEdit)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.checkBox = CheckBox(self.groupBox_4)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout_2.addWidget(self.checkBox)
        self.checkBox_2 = CheckBox(self.groupBox_4)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.verticalLayout_2.addWidget(self.checkBox_2)
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
        self.groupBox_4.setTitle(QtGui.QApplication.translate("ILineEdit", "Date settings", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("ILineEdit", "Default to current date", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-defaulttonow", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setText(QtGui.QApplication.translate("ILineEdit", "Include seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("ILineEdit", "Triggered pillows", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-groupbox-triggeredpillows", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("ILineEdit", "Enable logic", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setProperty("template", QtGui.QApplication.translate("ILineEdit", "inspector-groupbox-enablelogic", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.buttons.checkBox import CheckBox
from wallaby.frontends.qt.widgets.containers.groupBox import GroupBox

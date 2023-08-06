# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/widgets/prefs/prefSheet.ui'
#
# Created: Mon Nov 26 16:21:03 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PrefSheet(object):
    def setupUi(self, PrefSheet):
        PrefSheet.setObjectName(_fromUtf8("PrefSheet"))
        PrefSheet.resize(530, 296)
        PrefSheet.setMinimumSize(QtCore.QSize(400, 0))
        PrefSheet.setWindowOpacity(1.0)
        self.verticalLayout_2 = QtGui.QVBoxLayout(PrefSheet)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(PrefSheet)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setStyleSheet(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.toolbar = QtGui.QWidget(self.groupBox)
        self.toolbar.setObjectName(_fromUtf8("toolbar"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.toolbar)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setMargin(0)
        self.horizontalLayout_4.setMargin(0)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.widget = QtGui.QWidget(self.toolbar)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(0, 50))
        self.widget.setAutoFillBackground(False)
        self.widget.setStyleSheet(_fromUtf8("background: transparent;"))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.edit = QtGui.QPushButton(self.widget)
        self.edit.setMinimumSize(QtCore.QSize(24, 24))
        self.edit.setMaximumSize(QtCore.QSize(24, 24))
        self.edit.setAutoFillBackground(False)
        self.edit.setStyleSheet(_fromUtf8("QPushButton {\n"
"     border: 2px solid #8f8f91;\n"
"     border-radius: 6px;\n"
"     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                       stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
" }\n"
"\n"
" QPushButton:pressed {\n"
"     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                       stop: 0 #dadbde, stop: 1 #f6f7fa);\n"
" }\n"
"\n"
" QPushButton:flat {\n"
"     border: none; /* no border for a flat push button */\n"
" }\n"
"\n"
" QPushButton:default {\n"
"     border-color: navy; /* make the default button prominent */\n"
" }"))
        self.edit.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/lock_locked.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/lock_unlocked.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/lock_unlocked.png")), QtGui.QIcon.Disabled, QtGui.QIcon.On)
        self.edit.setIcon(icon)
        self.edit.setIconSize(QtCore.QSize(16, 16))
        self.edit.setCheckable(True)
        self.edit.setDefault(False)
        self.edit.setFlat(True)
        self.edit.setObjectName(_fromUtf8("edit"))
        self.horizontalLayout_2.addWidget(self.edit)
        self.moveDown = QtGui.QPushButton(self.widget)
        self.moveDown.setMinimumSize(QtCore.QSize(24, 24))
        self.moveDown.setMaximumSize(QtCore.QSize(24, 24))
        self.moveDown.setStyleSheet(_fromUtf8("QPushButton {\n"
"     border: 2px solid #8f8f91;\n"
"     border-radius: 6px;\n"
"     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                       stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
" }\n"
"\n"
" QPushButton:pressed {\n"
"     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                       stop: 0 #dadbde, stop: 1 #f6f7fa);\n"
" }\n"
"\n"
" QPushButton:flat {\n"
"     border: none; /* no border for a flat push button */\n"
" }\n"
"\n"
" QPushButton:default {\n"
"     border-color: navy; /* make the default button prominent */\n"
" }"))
        self.moveDown.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/arrow_down.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.moveDown.setIcon(icon1)
        self.moveDown.setFlat(True)
        self.moveDown.setObjectName(_fromUtf8("moveDown"))
        self.horizontalLayout_2.addWidget(self.moveDown)
        self.moveUp = QtGui.QPushButton(self.widget)
        self.moveUp.setMinimumSize(QtCore.QSize(24, 24))
        self.moveUp.setMaximumSize(QtCore.QSize(24, 24))
        self.moveUp.setStyleSheet(_fromUtf8("QPushButton {\n"
"     border: 2px solid #8f8f91;\n"
"     border-radius: 6px;\n"
"     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                       stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
" }\n"
"\n"
" QPushButton:pressed {\n"
"     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                       stop: 0 #dadbde, stop: 1 #f6f7fa);\n"
" }\n"
"\n"
" QPushButton:flat {\n"
"     border: none; /* no border for a flat push button */\n"
" }\n"
"\n"
" QPushButton:default {\n"
"     border-color: navy; /* make the default button prominent */\n"
" }"))
        self.moveUp.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/arrow_up.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.moveUp.setIcon(icon2)
        self.moveUp.setFlat(True)
        self.moveUp.setObjectName(_fromUtf8("moveUp"))
        self.horizontalLayout_2.addWidget(self.moveUp)
        self.remove = QtGui.QPushButton(self.widget)
        self.remove.setMinimumSize(QtCore.QSize(24, 24))
        self.remove.setMaximumSize(QtCore.QSize(24, 24))
        self.remove.setStyleSheet(_fromUtf8("QPushButton {\n"
"     border: 2px solid #8f8f91;\n"
"     border-radius: 6px;\n"
"     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                       stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
" }\n"
"\n"
" QPushButton:pressed {\n"
"     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                       stop: 0 #dadbde, stop: 1 #f6f7fa);\n"
" }\n"
"\n"
" QPushButton:flat {\n"
"     border: none; /* no border for a flat push button */\n"
" }\n"
"\n"
" QPushButton:default {\n"
"     border-color: navy; /* make the default button prominent */\n"
" }"))
        self.remove.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/delete.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove.setIcon(icon3)
        self.remove.setFlat(True)
        self.remove.setObjectName(_fromUtf8("remove"))
        self.horizontalLayout_2.addWidget(self.remove)
        self.dragLabel = DragLabel(self.widget)
        self.dragLabel.setMinimumSize(QtCore.QSize(20, 20))
        self.dragLabel.setMaximumSize(QtCore.QSize(20, 20))
        self.dragLabel.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        self.dragLabel.setStyleSheet(_fromUtf8("QLabel {\n"
"     border-radius: 6px;\n"
"     background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                       stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
" }"))
        self.dragLabel.setPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/move.png")))
        self.dragLabel.setScaledContents(True)
        self.dragLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.dragLabel.setObjectName(_fromUtf8("dragLabel"))
        self.horizontalLayout_2.addWidget(self.dragLabel)
        self.horizontalLayout_4.addWidget(self.widget)
        self.verticalLayout.addWidget(self.toolbar)
        self.content = QtGui.QWidget(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.content.sizePolicy().hasHeightForWidth())
        self.content.setSizePolicy(sizePolicy)
        self.content.setAutoFillBackground(False)
        self.content.setObjectName(_fromUtf8("content"))
        self.verticalLayout.addWidget(self.content)
        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(PrefSheet)
        QtCore.QMetaObject.connectSlotsByName(PrefSheet)

    def retranslateUi(self, PrefSheet):
        PrefSheet.setWindowTitle(QtGui.QApplication.translate("PrefSheet", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("PrefSheet", "GroupBox", None, QtGui.QApplication.UnicodeUTF8))
        self.toolbar.setToolTip(QtGui.QApplication.translate("PrefSheet", "edit", None, QtGui.QApplication.UnicodeUTF8))
        self.moveDown.setToolTip(QtGui.QApplication.translate("PrefSheet", "move down", None, QtGui.QApplication.UnicodeUTF8))
        self.moveUp.setToolTip(QtGui.QApplication.translate("PrefSheet", "move up", None, QtGui.QApplication.UnicodeUTF8))
        self.remove.setToolTip(QtGui.QApplication.translate("PrefSheet", "Remove", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.drag.dragLabel import DragLabel
from . import resource_rc

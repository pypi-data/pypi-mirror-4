# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/widgets/prefs/prefController.ui'
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

class Ui_PrefController(object):
    def setupUi(self, PrefController):
        PrefController.setObjectName(_fromUtf8("PrefController"))
        PrefController.resize(506, 701)
        self.verticalLayout_2 = QtGui.QVBoxLayout(PrefController)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.widget_3 = QtGui.QWidget(PrefController)
        self.widget_3.setObjectName(_fromUtf8("widget_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(self.widget_3)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.presets = ComboBox(self.widget_3)
        self.presets.setMinimumSize(QtCore.QSize(200, 0))
        self.presets.setEditable(True)
        self.presets.setInsertPolicy(QtGui.QComboBox.NoInsert)
        self.presets.setObjectName(_fromUtf8("presets"))
        self.horizontalLayout_2.addWidget(self.presets)
        self.loadPresetButton = ActionButton(self.widget_3)
        self.loadPresetButton.setObjectName(_fromUtf8("loadPresetButton"))
        self.horizontalLayout_2.addWidget(self.loadPresetButton)
        self.savePresetButton = ActionButton(self.widget_3)
        self.savePresetButton.setObjectName(_fromUtf8("savePresetButton"))
        self.horizontalLayout_2.addWidget(self.savePresetButton)
        self.verticalLayout_2.addWidget(self.widget_3)
        self.scrollArea = QtGui.QScrollArea(PrefController)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 504, 599))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.content = QtGui.QWidget(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.content.sizePolicy().hasHeightForWidth())
        self.content.setSizePolicy(sizePolicy)
        self.content.setObjectName(_fromUtf8("content"))
        self.verticalLayout.addWidget(self.content)
        self.widget_2 = QtGui.QWidget(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.verticalLayout.addWidget(self.widget_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.widget = QtGui.QWidget(PrefController)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.prefApplyButton = ActionButton(self.widget)
        self.prefApplyButton.setObjectName(_fromUtf8("prefApplyButton"))
        self.horizontalLayout.addWidget(self.prefApplyButton)
        self.prefRollbackButton = ActionButton(self.widget)
        self.prefRollbackButton.setObjectName(_fromUtf8("prefRollbackButton"))
        self.horizontalLayout.addWidget(self.prefRollbackButton)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.prefSelect = QtGui.QComboBox(self.widget)
        self.prefSelect.setMinimumSize(QtCore.QSize(150, 0))
        self.prefSelect.setEditable(False)
        self.prefSelect.setInsertPolicy(QtGui.QComboBox.InsertAtBottom)
        self.prefSelect.setFrame(True)
        self.prefSelect.setObjectName(_fromUtf8("prefSelect"))
        self.horizontalLayout.addWidget(self.prefSelect)
        self.prefAdd = QtGui.QPushButton(self.widget)
        self.prefAdd.setMaximumSize(QtCore.QSize(32, 32))
        self.prefAdd.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.prefAdd.setIcon(icon)
        self.prefAdd.setIconSize(QtCore.QSize(24, 24))
        self.prefAdd.setFlat(True)
        self.prefAdd.setObjectName(_fromUtf8("prefAdd"))
        self.horizontalLayout.addWidget(self.prefAdd)
        self.verticalLayout_2.addWidget(self.widget)

        self.retranslateUi(PrefController)
        QtCore.QMetaObject.connectSlotsByName(PrefController)

    def retranslateUi(self, PrefController):
        PrefController.setWindowTitle(QtGui.QApplication.translate("PrefController", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PrefController", "Presets:", None, QtGui.QApplication.UnicodeUTF8))
        self.loadPresetButton.setText(QtGui.QApplication.translate("PrefController", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.savePresetButton.setText(QtGui.QApplication.translate("PrefController", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.prefApplyButton.setText(QtGui.QApplication.translate("PrefController", "apply", None, QtGui.QApplication.UnicodeUTF8))
        self.prefRollbackButton.setText(QtGui.QApplication.translate("PrefController", "cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("PrefController", "Preference sheets", None, QtGui.QApplication.UnicodeUTF8))
        self.prefAdd.setToolTip(QtGui.QApplication.translate("PrefController", "Add", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.combo.comboBox import ComboBox
from wallaby.frontends.qt.widgets.buttons.actionButton import ActionButton
from . import resource_rc

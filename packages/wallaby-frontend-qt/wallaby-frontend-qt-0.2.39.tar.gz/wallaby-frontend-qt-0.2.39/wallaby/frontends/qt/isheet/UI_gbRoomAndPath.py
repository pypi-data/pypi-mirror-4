# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/gbRoomAndPath.ui'
#
# Created: Sun Dec  2 12:36:08 2012
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
        GbRoomAndPath.resize(94, 54)
        self.verticalLayout = QtGui.QVBoxLayout(GbRoomAndPath)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = Widget(GbRoomAndPath)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = Widget(GbRoomAndPath)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.verticalLayout.addWidget(self.widget_2)

        self.retranslateUi(GbRoomAndPath)
        QtCore.QMetaObject.connectSlotsByName(GbRoomAndPath)

    def retranslateUi(self, GbRoomAndPath):
        GbRoomAndPath.setWindowTitle(QtGui.QApplication.translate("GbRoomAndPath", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.widget.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-container-room", None, QtGui.QApplication.UnicodeUTF8))
        self.widget_2.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-container-path", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.containers.widget import Widget

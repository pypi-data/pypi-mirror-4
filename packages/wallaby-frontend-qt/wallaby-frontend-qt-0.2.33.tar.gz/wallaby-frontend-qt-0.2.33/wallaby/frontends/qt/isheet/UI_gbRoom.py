# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/dominik/Documents/Projekte/wallaby/wallaby-frontend-qt/wallaby/frontends/qt/isheet/gbRoom.ui'
#
# Created: Sun Dec  2 12:36:27 2012
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
        GbRoomAndPath.resize(92, 24)
        self.verticalLayout = QtGui.QVBoxLayout(GbRoomAndPath)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = Widget(GbRoomAndPath)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(GbRoomAndPath)
        QtCore.QMetaObject.connectSlotsByName(GbRoomAndPath)

    def retranslateUi(self, GbRoomAndPath):
        GbRoomAndPath.setWindowTitle(QtGui.QApplication.translate("GbRoomAndPath", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.widget.setProperty("template", QtGui.QApplication.translate("GbRoomAndPath", "inspector-container-room", None, QtGui.QApplication.UnicodeUTF8))

from wallaby.frontends.qt.widgets.containers.widget import Widget

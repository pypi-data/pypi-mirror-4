# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from wallaby.frontends.qt.widgets.drag.dragLogic import *

class LockLayer(QtGui.QWidget, DragLogic):
    Pixmap = None
    DragPixmap = None

    def __init__(self):
        QtGui.QWidget.__init__(self)
        DragLogic.__init__(self)

        if LockLayer.Pixmap == None:
            LockLayer.Pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(':/icons/images/schloss.png').scaled(65, 65))

        self._pen = QtGui.QPen(QtGui.QColor(255, 0, 0, 128))

        if LockLayer.DragPixmap == None:
            LockLayer.DragPixmap = QtGui.QPixmap(':/icons/images/move.png')

    def pixmap(self):
        return LockLayer.DragPixmap

    def paintEvent(self, e):
        p = QtGui.QPainter(self)
        p.setBrush(QtGui.QColor(128,128,128, 128))
        p.setPen(QtCore.Qt.NoPen)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.drawRoundedRect(0,0,self.width(), self.height(), 5,5) 
        p.setPen(self._pen)
        # p.drawText(0,0,self.width(), self.height(), QtCore.Qt.AlignCenter, "BLA")
        p.drawPixmap(self.width()/2-LockLayer.Pixmap.width()/2, self.height()/2-LockLayer.Pixmap.height()/2, LockLayer.Pixmap)

    def mouseDoubleClickEvent(self, e):
        self.parent().unlock()
        e.accept()

    def mousePressEvent(self, e):
        DragLogic.mousePressEvent(self, e)

    def mouseMoveEvent(self, e):
        DragLogic.mouseMoveEvent(self, e)

# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *
from wallaby.common.sets import OrderedSet

class WallabyPopup(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle("Wallaby - properties")

        flags = self.windowFlags()

        self.setMinimumSize(300, 200)
        self.setMaximumSize(300, 200)

        self.hide()

class WallabyOverlay(QtGui.QWidget):
    Pixmap = None
    Brushes = None

    RoomBrushes = {}
    NextBrush = 0

    @classmethod
    def resetColors(cls):
        cls.Brushes = None
        cls.NextBrush = 0
        cls.RoomBrushes = {}

    @classmethod
    def getColor(cls, room, width=None, height=None):
        if cls.Brushes == None:
            cls.Brushes = (
                ( QtGui.QColor(128,   0, 0  , 128), QtGui.QColor(128, 0  , 0  , 200) ), 
                ( QtGui.QColor(0  , 128, 0  , 128), QtGui.QColor(0  , 128, 0  , 200) ), 
                ( QtGui.QColor(0  , 0  , 128, 128), QtGui.QColor(0  , 0  , 128, 200) ), 
                ( QtGui.QColor(128, 128, 0  , 128), QtGui.QColor(128, 128, 0  , 200) ), 
                ( QtGui.QColor(0  , 128, 128, 128), QtGui.QColor(0  , 128, 128, 200) ), 
                ( QtGui.QColor(128, 0  , 128, 128), QtGui.QColor(128, 0  , 128, 200) ), 
                ( QtGui.QColor(192, 128, 64 , 128), QtGui.QColor(192, 128, 64 , 200) ), 
                ( QtGui.QColor(64 , 192, 128, 128), QtGui.QColor(64 , 192, 128, 200) ), 
                ( QtGui.QColor(128, 64 , 192, 128), QtGui.QColor(128, 64 , 192, 200) ), 
                ( QtGui.QColor(128, 128, 128, 128), QtGui.QColor(128, 128, 128, 200) )
            )

            cls.RoomBrushes[None] = 0
            cls.NextBrush = 1

        if width != None and isinstance(room, OrderedSet):
            cnt = len(room)
            if cnt >= 2:
                gradLL = QtGui.QLinearGradient(0, 0, width, height)
                gradHL = QtGui.QLinearGradient(0, 0, width, height)
                idx = 0.0
                cnt = float(cnt-1)
                for r in room:
                    gradLL.setColorAt(idx/cnt, cls.getColor(r)[0])
                    gradHL.setColorAt(idx/cnt, cls.getColor(r)[1])
                    idx += 1.0

                return (gradLL, gradHL)
            else:
                for r in room:  
                    room = r
                    break

        if isinstance(room, OrderedSet):
            return cls.Brushes[0]

        if room not in cls.RoomBrushes:
            cls.RoomBrushes[room] = cls.NextBrush
            cls.NextBrush += 1
            if cls.NextBrush >= len(cls.Brushes): cls.NextBrush = 1

        return cls.Brushes[cls.RoomBrushes[room]]

    def __init__(self, parent, host):
        QtGui.QWidget.__init__(self, parent)

        self._host = host

        if WallabyOverlay.Pixmap == None:
            WallabyOverlay.Pixmap = QtGui.QPixmap.fromImage(QtGui.QImage(':/images/images/wallaby.png').scaled(32, 32))

        self._hlPen = QtGui.QPen(QtGui.QColor(255, 255, 255, 222))
        self._llPen = QtGui.QPen(QtGui.QColor(255, 255, 255, 200))

        self._borderPen = QtGui.QPen(QtGui.QColor(0, 0, 0, 255))

        self._active = False
        self._showPixmap = False
        self._margin = 2
        self._label = ""
        self._room = None
        self._shortLabel = ""
        self._longLabel = ""
        self._baseGeometry = None
        self._anim = None
        self._lastWidth = None

        # self._popup = WallabyPopup(self)

    def host(self):
        return self._host

    def setBaseGeometry(self, geo):
        self._stopAnimation()

        self._baseGeometry = geo
        self.setGeometry(geo)

    def show(self):
        labels = self._host.overlayLabel()

        if len(labels) > 0:
            self._room = labels[0]
        else:
            self._room = None

        if len(labels) > 1: self._shortLabel = " | ".join(labels[1:])
        else: self._shortLabel = ""

        if self._room != None:
            if isinstance(self._room, OrderedSet):
                lst = self._room
                if None in lst: lst.remove(None)
                self._longLabel = "+".join(lst)
            else:
                self._longLabel = self._room
        else:   
            self._longLabel = "-"

        if self._shortLabel != "":
            self._longLabel += " | " + self._shortLabel
        else:
            self._shortLabel = self._longLabel

        self._label = self._shortLabel
        self._lastWidth = None

        self.setMouseTracking(True)
        QtGui.QWidget.show(self)
        self.repaint()

    def setBrushes(self):
        brushes = WallabyOverlay.getColor(self._room, self.width(), self.height())
        if self._active:
            self._pen = self._hlPen
            self._brush = brushes[1]
        else:
            self._pen = self._llPen
            self._brush = brushes[0]

    def hide(self):
        self.setMouseTracking(False)
        QtGui.QWidget.hide(self)

    def enterEvent(self, e):
        self._stopAnimation()

        fm = QtGui.QFontMetrics(self.font())

        self.raise_()
        self._active = True
        self.setBrushes()

        self._label = self._longLabel

        geo = self.geometry()

        w = geo.width()
        dw = fm.width(self._label) + 20 - w

        if dw > 0:
            w += dw
            geo.setWidth(w)

            offset = dw/2

            if self.pos().x() - offset + w > FX.mainWindow.width():
                offset = - (FX.mainWindow.width() - self.pos().x() - w)

            geo.moveTo(self.pos().x()-offset, self.pos().y())


        if geo != self.geometry():
            self._anim = QtCore.QPropertyAnimation(self ,"geometry");
            self._anim.setDuration(500)
            self._anim.setStartValue(self.geometry())
            self._anim.setEndValue(geo)
            self._anim.start()
        else:
            self.repaint()

    def _stopAnimation(self):
        if self._anim != None and self._anim.state() == QtCore.QAbstractAnimation.Running:
            self._anim.stop()

        self._anim = None

    def leaveEvent(self, e):
        self._stopAnimation()

        self._active = False
        self.setBrushes()

        self._label = self._shortLabel

        if self._baseGeometry != None and self.geometry() != self._baseGeometry:
            self._anim = QtCore.QPropertyAnimation(self ,"geometry");
            self._anim.setDuration(300)
            self._anim.setStartValue(self.geometry())
            self._anim.setEndValue(self._baseGeometry)
            self._anim.start()
        else:
            self.repaint()

    def paintEvent(self, e):
        if self.width() != self._lastWidth:
            self.setBrushes()

        self._lastWidth = self.width()

        p = QtGui.QPainter(self)
        p.setBrush(self._brush)
        p.setPen(self._borderPen)
            
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        p.drawRoundedRect(0,0,self.width(), self.height(), 5,5) 
        p.setPen(self._pen)
        label = self._label

        x = self._margin
        y = self._margin  
        if self._showPixmap: 
            x += self._margin + WallabyOverlay.Pixmap.width()

        p.drawText(x, y, self.width()-x-self._margin, self.height()-y-self._margin, QtCore.Qt.AlignCenter, label)

        if self._showPixmap:
            p.drawPixmap(self._margin, self._margin, WallabyOverlay.Pixmap)

    def mousePressEvent(self, e):
        FX.mainWindow.openConfig(self._host)
        e.accept()

    def mouseDoubleClickEvent(self, e):
        e.ignore()

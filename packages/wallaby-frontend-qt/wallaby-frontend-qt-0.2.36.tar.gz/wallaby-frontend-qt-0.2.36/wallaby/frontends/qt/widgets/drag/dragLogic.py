# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

import json
from wallaby.common.draggable import *

class DragLogic(object):
    def __init__(self):
        self._dragStartPosition = None

    def mousePressEvent(self, event):
        if event.button() & QtCore.Qt.LeftButton:
            self._dragStartPosition = event.pos()

    def mouseMoveEvent(self, event):
        if not event.buttons() & QtCore.Qt.LeftButton: return
        if (event.pos() - self._dragStartPosition).manhattanLength() < QtGui.QApplication.startDragDistance(): return

        p = self.parent()
        while not isinstance(p, Draggable) and not p is None:
            p = p.parent()
        if p is None:
            return

        drag = QtGui.QDrag(self)

        mimeData = QtCore.QMimeData()
        mimeData.setText(p.dragURL())
        # mimeData.setUrls([QtCore.QUrl(p.dragURL())])
        p.dragCustom(mimeData)

        drag.setPixmap(self.pixmap())
        drag.setMimeData(mimeData)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction, QtCore.Qt.MoveAction)

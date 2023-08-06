# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *
from ..baseWidget import *
from UI_prefSheet import *
from functools import partial
import json
from wallaby.common.draggable import *
from lockLayer import LockLayer

class PrefSheet(QtGui.QWidget, Ui_PrefSheet, BaseWidget, Draggable):
    __metaclass__ = QWallabyMeta

    room = Meta.property("string")
    path = Meta.property("string")

    lockLayerTopMargin = 18

    Up = None
    Down = None

    # def __del__(self):
    #    print "!!!DELETING!!!", self

    def overlayRect(self):
        r = BaseWidget.overlayRect(self)
        # r.moveTo(r.x(), r.height()-20)
        r.setHeight(min(r.height(), 20))
        return r

    def __init__(self, type, room, path, controller, idx, title, locked=True):
        QtGui.QWidget.__init__(self)
        BaseWidget.__init__(self, QtGui.QWidget)

        self.setupUi(self)

        self.room = room
        self._type = type
        self._idx = idx
        self._path = path
        self.path = path + "." + unicode(self._idx)
        self._controller = controller
        self.groupBox.setTitle(title)

        self.remove.clicked.connect(self.removePrefWidget)

        self.moveUp.clicked.connect(partial(self.movePrefWidget, True))
        self.moveDown.clicked.connect(partial(self.movePrefWidget, False))

        # self.content.setEnabled(False)
        self.edit.clicked.connect(self.editPrefWidget)

        self.setAcceptDrops(True)

        if PrefSheet.Up == None:
            PrefSheet.Up = QtGui.QPixmap(':icons/images/arrow_up.png')

        if PrefSheet.Down == None:
            PrefSheet.Down = QtGui.QPixmap(':icons/images/arrow_down.png')

        self._dragging = False
        self._direction = True
        self._ensureVisibleCall = None

        self.groupBox.layout().takeAt(0)
        self.toolbar.setParent(self)
        self.toolbar.move(300, -15)
        self.toolbar.setMinimumHeight(50)

        self._lockLayer = LockLayer()
        self._lockLayer.setParent(self)
        self._lockLayer.move(0,PrefSheet.lockLayerTopMargin)

        if locked:
            self.lock() 
        else:
            self.unlock()
        
        self.update()

    def unlock(self):
        self._lockLayer.hide()  
        self.content.setEnabled(True)
        self.edit.setChecked(True)

    def lock(self):
        self._lockLayer.show()  
        self.content.setEnabled(False)
        self.edit.setChecked(False)

    def resizeEvent(self, e):
        QtGui.QWidget.resizeEvent(self, e)
        if self.height() > PrefSheet.lockLayerTopMargin:
            self._lockLayer.setMinimumHeight(self.height()-PrefSheet.lockLayerTopMargin)
            self._lockLayer.setMinimumWidth(self.width())
            self._lockLayer.setMaximumHeight(self.height()-PrefSheet.lockLayerTopMargin)
            self._lockLayer.setMaximumWidth(self.width())

    def dragCustom(self, mimeData):
        mimeData.setData('wallaby/pref', unicode(self._idx))

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("wallaby/pref"):
            idx = int(event.mimeData().data("wallaby/pref"))
            self._checkDragEvent(event)

            if idx == self._idx: return
            event.acceptProposedAction()

    def _checkDragEvent(self, event):
        if event.mimeData().hasFormat("wallaby/pref"):
            if self._ensureVisibleCall is None:
                from twisted.internet import reactor
                self._ensureVisibleCall = reactor.callLater(0.5, self._callEnsureVisible)

            idx = int(event.mimeData().data("wallaby/pref"))
            if idx == self._idx: 
                self._rejectDragEvent(event)
                return

            if event.pos().y() < self.height()/2:
                if idx == self._idx - 1: 
                    self._rejectDragEvent(event)
                    return

                self._direction = True
            else:
                if idx == self._idx + 1: 
                    self._rejectDragEvent(event)
                    return

                self._direction = False

            self._dragging = True
            event.acceptProposedAction()

            self.update()
            return 
        self._rejectDragEvent(event)

    def _rejectDragEvent(self, event):
        if self._dragging:
            self._dragging = False
            self.update()

    def _callEnsureVisible(self):
        self._ensureVisibleCall = None
        self._controller.scrollArea.ensureWidgetVisible(self, 50, 100)

    def dragMoveEvent(self, event):
        self._checkDragEvent(event)
    
    def dragLeaveEvent(self, event):
        self._dragging = False
        if self._ensureVisibleCall is not None:
            self._ensureVisibleCall.cancel()
            self._ensureVisibleCall = None

        self.update()

    def dropEvent(self, event):
        self._dragging = False

        if self._ensureVisibleCall is not None:
            self._ensureVisibleCall.cancel()
            self._ensureVisibleCall = None

        idx = int(event.mimeData().data("wallaby/pref"))
        if event.pos().y() < self.height()/2:
            self._controller.move(idx, self._idx)
        else:
            self._controller.move(idx, self._idx+1)

        event.acceptProposedAction()
        self.releaseMouse()
        self.setMouseTracking(False)
        self.update()

    def paintEvent(self, e):
        if self._dragging:
            p = QtGui.QPainter(self)
            if self._direction:
                p.drawPixmap(self.width()/2.0-PrefSheet.Up.width()/2.0,20, PrefSheet.Up)
            else:
                p.drawPixmap(self.width()/2.0-PrefSheet.Down.width()/2.0,self.height()-PrefSheet.Down.height(), PrefSheet.Down)

    def type(self):
        return self._type

    def dragText(self):
        if self._controller._pref == None: return None
        return json.dumps(self._controller._pref.document().get(self.path))

    def dragURL(self):
        return self._controller._pref.document().url()

    def editPrefWidget(self):
        if self.edit.isChecked():
            self.unlock()
        else:
            self.lock()

    def movePrefWidget(self, direction, state):
        self._controller.movePrefSheet(self._idx, direction)

    def decrementIndex(self):
        self.setIndex(self._idx - 1)

    def incrementIndex(self):
        self.setIndex(self._idx + 1)

    def setIndex(self, idx):
        self._idx = idx
        self.path = self._path + "." + unicode(self._idx)

        widgets = self.findChildren(BaseWidget)
        for w in widgets:
            w.deregister()
            w.register()

    def removePrefWidget(self):
        self._controller.remove(self._idx)

    def configure(self, config):
        pass


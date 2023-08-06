# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..baseWidget import *
from wallaby.pf.peer.stack import *

class Controller(QtGui.QWidget, BaseWidget):
    __metaclass__ = QWallabyMeta

    room = Meta.property("string")

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QWidget, *args)
        self._stack = None

        self._layerNames = {}
        self._layerNames['root'] = self

        self._layers = []
        self._layers.append(self)

    def register(self):
        self._stack = Stack(self.room, self)

        for layer in self._layers:
            if layer != self:
                layer.register()

    def deregister(self, remove=False):
        if self._stack != None: self._stack.destroy(remove)
        self._stack = None

        for layer in self._layers:
            if layer != self:
                layer.deregister(remove)

    # def resizeEvent(self, event):
    #     QtGui.QWidget.resizeEvent(self, event)

    #     for layer in self._layers:
    #         if layer != self:
    #             layer.resize(self.width(), self.height())

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(255,0,0,255))
        r = QtCore.QRectF(0,0,self.width(),self.height())
        painter.drawRect(r)

    def addLayer(self, layer, setZeroContentsMargins = True, group=None, hidden=False):
        name = layer._name
        if name == None: return

        topLayer = self._layers[len(self._layers)-1]
    
        l = QtGui.QVBoxLayout(topLayer)

        if setZeroContentsMargins == True:
            l.setContentsMargins(0,0,0,0)

        l.addWidget(layer)
        layer._controller = self

        self._layerNames[name] = layer
        self._layers.append(layer)
        layer._group = group

        if hidden:
            self.hideLayer(name)
        else:
            self.showLayer(name)

    def showLayer(self, name):
        currLayer = None
        for layer in self._layers:
            if layer != self:
                if layer._name == name:
                    currLayer = layer
                    break
        for layer in self._layers:
            if layer != self and layer._group != None and currLayer != None:
                if layer._group == currLayer._group and layer._name != name:
                    layer.setDisplayingContent(False)

        self._setLayerDisplayingContent(name, True)

    def hideLayer(self, name):
        self._setLayerDisplayingContent(name, False)

    def _setLayerDisplayingContent(self, name, displayingContent):
        if name == None: return

        if name in self._layerNames:
            layer = self._layerNames[name]
            if layer: layer.setDisplayingContent(displayingContent)

            self.update() #trigger repaint

    def enableLayer(self, name):
        self._setLayerUserinteractionEnabled(True)

    def disableLayer(self, name):
        self._setLayerUserinteractionEnabled(False)

    def _setLayerUserinteractionEnabled(self, name, userinteractionEnabled):
        if name == None: return

        if name in self._layerNames:
            layer = self._layerNames[name]
            if layer: layer.setUserinteractionEnabled(userinteractionEnabled)

    def isVisible(self, name):
        for layer in self._layers:
            if layer != self:
                if layer._group == name or layer._name == name:
                    if layer._displayingContent:
                        return layer._displayingContent
        return False

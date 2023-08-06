# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

class Layer(QtGui.QWidget):
    def __init__(self, name, *args):
        QtGui.QWidget.__init__(self, *args)

        self._name = name
        self._displayingContent = False
        self._userinteractionEnabled = True
        self._group = None
    

    def setDisplayingContent(self, displayingContent):
        self._displayingContent = displayingContent

    def setUserinteractionEnabled(self, userinteractionEnabled):
        self._userinteractionEnabled = userinteractionEnabled

    def userinteractionEnabled(self):
        return self._displayingContent == True and self._userinteractionEnabled == True

    def register(self):
        pass

    def deregister(self, remove=False):
        pass

    def paintEvent(self, event):
        if self._displayingContent == True:
            self.layerPaintEvent(event)

    def layerPaintEvent(self, event):
        pass

    def keyPressEvent(self, event):
        if self.userinteractionEnabled() == True:
            self.layerKeyPressEvent(event)
        else:
            event.ignore()

    def layerKeyPressEvent(self, event):
        self.parentWidget().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.userinteractionEnabled() == True:
            self.layerKeyReleaseEvent(event)
        else:
            event.ignore()

    def layerKeyReleaseEvent(self, event):
        self.parentWidget().keyReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.userinteractionEnabled() == True:
            self.layerMouseMoveEvent(event)
        else:
            event.ignore()

    def layerMouseMoveEvent(self, event):
        self.parentWidget().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if self.userinteractionEnabled() == True:
            self.layerMousePressEvent(event)
        else:
            event.ignore()

    def layerMousePressEvent(self, event):
        self.parentWidget().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.userinteractionEnabled() == True:
            self.layerMouseDoubleClickEvent(event)
        else:
            event.ignore()

    def layerMouseDoubleClickEvent(self, event):
        self.parentWidget().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if self.userinteractionEnabled() == True:
            self.layerMouseReleaseEvent(event)
        else:
            event.ignore()

    def layerMouseReleaseEvent(self, event):
        event.ignore()

    def wheelEvent(self, event):
        if self.userinteractionEnabled() == True:
            self.layerWheelEvent(event)
        else:
            event.ignore()

    def layerWheelEvent(self, event):
        self.parentWidget().wheelEvent(event)

    def hoverEvent(self, event):
        if self.userinteractionEnabled() == True:
            self.layerHoverEvent(event)
        else:
            event.ignore()

    def layerHoverEvent(self, event):
        self.parentWidget().hoverEvent(event)

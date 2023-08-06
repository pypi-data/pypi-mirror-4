# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.imageViewer import *
from wallaby.pf.peer.imageEditor import *

class ImageLabel(QtGui.QLabel, BaseWidget, EnableLogic, ViewLogic, EditLogic):
    __metaclass__ = QWallabyMeta

    def __init__(self, *args):
        QtGui.QLabel.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QLabel, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, ImageViewer, self._changeImage)
        EditLogic.__init__(self, ImageEditor, self.currentImage)

        self._currentImage = None
        self._readOnly = True
        self._imageName = None

        self._popup = None
        self._popupLabel = QtGui.QLabel()

    def createPopup(self):
        p = self._popup = QtGui.QMainWindow(FX.mainWindow)
        # p.setFixedSize(512, 512)
        p.setWindowTitle('Zoom Image')
        p.setCentralWidget(self._popupLabel)
        p.hide()

    def deregister(self, remove=True):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)
        EditLogic.register(self)

    def _resolve(self, value):
        self._changeImage(value)

    def setEnabled(self, enabled):
        self._readOnly = not enabled
        QtGui.QLabel.setEnabled(self, True)

    def currentImage(self):
        return self._currentImage, self._imageName

    def mouseDoubleClickEvent(self, e):
        if self._readOnly or self._editor == None: 
            if self._popup == None:
                self.createPopup()

            self._popup.show()
            self._popup.raise_()
            return

        name = QtGui.QFileDialog.getOpenFileName(self, "Select new image", "", "Images (*.png *.jpg *.jpeg)")
        if name == None or len(name) == 0:
            return

        imgName = unicode(name)
        import os.path
        imgName = os.path.basename(imgName)
        self._imageName = imgName

        img = QtGui.QImage(name)
        self._updateImage(img)
        self._updatePopup(img)

        ba = QtCore.QByteArray()
        buffer = QtCore.QBuffer(ba)
        img.save(buffer, "PNG")

        self._currentImage = ba.data()
        self._editor._fieldChanged()

    def _updatePopup(self, img):
        p = QtGui.QPixmap()

        if img != None:
            p.convertFromImage(img)

        self._popupLabel.setPixmap(p)

    def _updateImage(self, img):
        p = QtGui.QPixmap()

        if img != None:
            p.convertFromImage(img)

        self.setPixmap(p)

    def _changeImage(self, d, name):
        self._imageName = name

        if d == None:
            self._updateImage(None)
            return

        d.addCallback(self._doChangeImage)

    def _doChangeImage(self, data):
        if data == None or len(data) == 0:
            self._updateImage(None)
            return

        self._currentImage = data

        img = QtGui.QImage.fromData(self._currentImage)
        self._updatePopup(img)

        img = img.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        self._updateImage(img)

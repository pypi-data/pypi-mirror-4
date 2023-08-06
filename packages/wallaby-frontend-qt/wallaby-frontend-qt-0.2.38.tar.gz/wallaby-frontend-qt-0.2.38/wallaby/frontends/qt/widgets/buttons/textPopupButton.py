# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *
import sys

from ..baseWidget import *

from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.editor import *
from ..logics import *

class TextPopupButton(QtGui.QPushButton, BaseWidget, EnableLogic, ViewLogic, EditLogic):
    __metaclass__ = QWallabyMeta

    title = Meta.property("string")

    def __init__(self, *args):
        QtGui.QPushButton.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QPushButton, *args)
        EnableLogic.__init__(self)

        self._changed = True

        self._plainTextEdit = QtGui.QPlainTextEdit()
        self._plainTextEdit.textChanged.connect(self._textChanged)

        self._dialog = QtGui.QDialog(self)
        self._dialog.setWindowFlags(self._dialog.windowFlags() | QtCore.Qt.Tool)

        layout = QtGui.QHBoxLayout()
        self._dialog.setLayout(layout)
        self._dialog.hide()

        layout.addWidget(self._plainTextEdit)

        ViewLogic.__init__(self, Viewer, self._setValue)
        EditLogic.__init__(self, Editor, self._plainTextEdit.toPlainText)

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)
        EditLogic.register(self)

        if self.title != None:
            self._dialog.setWindowTitle(self.title)

        self.clicked.connect(self._buttonClicked)

    def _setEnabled(self, enabled):
        if self.hideIfDisabled:
            self.setVisible(enabled)
        else:
            self._plainTextEdit.setReadOnly(not enabled)

    def _buttonClicked(self, state):
        if self._dialog.isHidden():
            self._dialog.show()
            self._dialog.raise_()
        else:
            self._dialog.hide()

    def _resolve(self, value, **ka):
        self._setValue(value)
        if self._editor: self._editor._resolve(**ka)

    def _setValue(self, val):
        if self._plainTextEdit.toPlainText() != val:
            self._changed = False
            self._plainTextEdit.setPlainText(val)
            self._changed = True

    def _textChanged(self):
        if self._editor and self._changed:
            self._editor._fieldChanged()

    def _docCB(self, document):
        print "doc", document
        print self.objectName()
        print "obj name", document.get(self.objectName())


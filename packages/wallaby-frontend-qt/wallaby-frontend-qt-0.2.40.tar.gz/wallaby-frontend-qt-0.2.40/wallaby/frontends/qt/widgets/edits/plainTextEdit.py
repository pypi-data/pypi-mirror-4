# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

import sys

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.editor import *

class PlainTextEdit(QtGui.QPlainTextEdit, BaseWidget, EnableLogic, ViewLogic, EditLogic):
    __metaclass__ = QWallabyMeta

    isJson  = Meta.property("bool", default=False)
    throwWhileEditing = Meta.property("bool", extended=True, default=True)

    def __init__(self, *args):
        QtGui.QPlainTextEdit.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QPlainTextEdit, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self._setValue)
        EditLogic.__init__(self, Editor, self._toPlainText)

        self._cb = None
        self._changed = True

        self._readOnly = self.isReadOnly()
        self.textChanged.connect(self._textChanged)

    def focusOutEvent ( self, event ):
        # self.setCursorWidth(0)

        if self._editor and self._changed:
            self._editor._fieldChanged()

        QtGui.QPlainTextEdit.focusOutEvent(self, event)

    def focusInEvent ( self, event ):
        # self.setCursorWidth(1)
        QtGui.QPlainTextEdit.focusInEvent(self, event)

    def _toPlainText (self):
        value = unicode(self.toPlainText())
       
        if self.isJson: 
            if value.startswith('{'):
                try:
                    import json
                    value = json.loads(value)
                except:           
                    pass
        else:
            return value

    def _setEnabled(self, enabled):
        if self._readOnly: return

        if self.hideIfDisabled:
            self.setVisible(enabled)
        else:
            self.setReadOnly(not enabled)

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self, raw=True)
        EditLogic.register(self)

    def _resolve(self, value, **ka):
        if value == None:
            self._setValue( "")
        else:
            self._setValue(value)

        if self._editor: self._editor._resolve(**ka)

    def _setValue(self, val):
        if isinstance(val, (str, unicode)):
            val = unicode(val)
        else:
            if val != None:
                if self.isJson:
                    try:
                        import json
                        val = json.dumps(val, sort_keys=True, indent=4, separators=(',', ': '))
                    except:
                        val = unicode(val)
                else:
                    val = unicode(val)
            else:
                val = u""

        if self.toPlainText() != val:
            self._changed = False
            self.setPlainText(val)
            self._changed = True

    def _textChanged(self):
        if self.throwWhileEditing and self._editor and self._changed:
            self._editor._fieldChanged()
        self._changed = True

    def _docCB(self, document):
        print "doc", document
        print self.objectName()
        print "obj name", document.get(self.objectName())


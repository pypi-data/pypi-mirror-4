# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

import sys

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.editor import *

class LineEdit(QtGui.QLineEdit, BaseWidget, EnableLogic, ViewLogic, EditLogic, EnterPillowLogic, ContextMenuLogic, TriggeredPillowsLogic):
    __metaclass__ = QWallabyMeta

    throwWhileEditing = Meta.property("bool", extended=True, default=True)
    triggers = Meta.property("list", readOnly=True, default=["", "changed","enter","finished","key"])

    def getMenuEntries(self): return ContextMenuLogic.getMenuEntries(self)

    def __init__(self, *args):
        QtGui.QLineEdit.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QLineEdit, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self._setText)
        EditLogic.__init__(self, Editor, self.text)
        EnterPillowLogic.__init__(self, self.returnPressed)
        TriggeredPillowsLogic.__init__(self)

        self._firstAccess = True
        self._readOnly = False

        self._changed = False

        from functools import partial
        self.textEdited.connect(self._textEdited)
        self.editingFinished.connect(self._editingFinished)
        self.returnPressed.connect(partial(self.trigger, "enter", None))

    def keyPressEvent(self, event):
        import wallaby.FXUI as FXUI 
        if self.trigger("key", FXUI.key_event_to_name(event)):
            event.accept()
        else:
            event.ignore()
            QtGui.QLineEdit.keyPressEvent(self, event)        

    def _textEdited(self, *args):
        if self.throwWhileEditing and self._changed:
            self.trigger("changed")
            if self._editor: self._editor._fieldChanged()

        self._changed = True

    def _editingFinished(self, *args):
        self.trigger("finished")

        if self._editor:
            self._editor._fieldChanged()

        self._changed = True

    def _setEnabled(self, enabled):
        if self._firstAccess:
            self._readOnly = self.isReadOnly()
            self._firstAccess = False

        if self._readOnly: return

        if self.hideIfDisabled:
            self.setVisible(enabled)
        else:
            self.setReadOnly(not enabled)

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)
        EnterPillowLogic.deregister(self, remove)
        TriggeredPillowsLogic.deregister(self, remove)

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)
        EditLogic.register(self, selectCallback=self._select)
        EnterPillowLogic.register(self)
        TriggeredPillowsLogic.register(self)

    def _resolve(self, value, **ka):
        if not value:
            self._setText("-")
        else:
            self._setText(value)

        if self._editor: self._editor._resolve(**ka)
        self._textEdited()

    def _select(self):
        self.setFocus()

    def _setText(self, val):
        if self.text() != val:
            self._changed = False
            self.setText(val)
            self._changed = True

    def _docCB(self, document):
        print self.objectName()

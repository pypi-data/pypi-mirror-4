# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

import sys

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.listPeer import *
from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.multiViewer import *
from wallaby.pf.peer.editor import *
from twisted.internet import defer

class ComboBox(QtGui.QComboBox, BaseWidget, EnableLogic, ViewLogic, EditLogic):
    __metaclass__ = QWallabyMeta

    isEditor = Meta.property("bool")
    source = Meta.property("string")
    sourcePath = Meta.property("string")

    selectPillow = Meta.property("string", extended=True)
    insertPillow = Meta.property("string", extended=True)

    isView = Meta.property("bool", extended=True)
    view           = Meta.property("string", extended=True)
    viewArguments  = Meta.property("dict", extended=True)
    viewIdentifier = Meta.property("string", extended=True)
    dataView       = Meta.property("bool", extended=True)

    viewPath = Meta.property("string", extended=True)
    viewDisplayPath = Meta.property("string", extended=True)
    throwWhileEditing = Meta.property("bool", extended=True)

    def __init__(self, *args):
        QtGui.QComboBox.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QComboBox, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self._setItemText)
        EditLogic.__init__(self, Editor, self._currentText)

        self.sourceVal = None
        self._changed = True
        self._lastValue = None

        self._subPath = None

        self._listPeer = None
        self._viewPeer = None
        self._multiViewer = None
        self._translate = {}
        self._translateReverse = {}
        self.currentIndexChanged.connect(self._selectOther)

    def _currentText(self):
        text = unicode(self.currentText())
        if text in self._translate:
            text = self._translate[text]

        return text

    def overlayLabel(self):
        label = BaseWidget.overlayLabel(self)
        if self.isView:
            label.append(self.view)
        else:
            path = self.sourcePath
            if path == None: path = 'titles'
            if self.source != None:
                label.append(self.source + ":" + path)
            else:
                label.append(path)
        
        return label

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        if self.lineEdit() != None: EditLogic.deregister(self, remove)

        if self._listPeer: self._listPeer.destroy(remove)
        self._listPeer = None

        if self._viewPeer: self._viewPeer.destroy(remove)
        self._viewPeer = None

        if self._multiViewer: self._multiViewer.destroy(remove)
        self._multiViewer = None

    def _textChanged(self, *args):
        if self.throwWhileEditing:
            self._editingFinished()

    def _editingFinished(self):
        if self._editor != None and self.lineEdit() != None and self._changed:
            self._editor._fieldChanged()
        if self.insertPillow != None:
            House.get(self.room).throw(self.insertPillow, unicode(self.lineEdit().text()))

    def changedCB(self, docID):
        # print "CHANGED:", docID
        pass

    def dataCB(self, result):
        from twisted.internet import reactor
        reactor.callLater(0, self._dataCB, result)

    @defer.inlineCallbacks
    def _dataCB(self, result):
        self._changed = False
        if result == None:
            self.clear()
            return

        viewDisplayPath = self.viewDisplayPath
        viewPath = self.viewPath
        if viewDisplayPath == None: viewDisplayPath = self.viewPath
        if viewDisplayPath == None: viewDisplayPath = "value"

        self._translate = {}
        self._translateReverse = {}

        if result.length() != self.count():
            self.clear()
            for i in range(result.length()):
                displayValue = yield result.deferredGetValue(i, viewDisplayPath)
                value = yield result.deferredGetValue(i, viewPath)
                if value != None:
                    self._translate[displayValue] = value
                    self._translateReverse[value] = displayValue
                    self.insertItem(i, displayValue)
        else:
            for i in range(result.length()):
                displayValue = yield result.deferredGetValue(i, viewDisplayPath)
                value = yield result.deferredGetValue(i, viewPath)
                if value != None:
                    self._translate[displayValue] = value
                    self._translateReverse[value] = displayValue
                    self.setItemText(i, displayValue)

        self._changed = True
        self._viewer._refresh(None, self.path) # Select path value

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)
        if self.isEditor != None: EditLogic.register(self, raw=True)

        if not self._registered:
            self._registered = True

            if self.lineEdit() != None:
                self.lineEdit().textChanged.connect(self._textChanged)
                self.lineEdit().editingFinished.connect(self._editingFinished)

        if self.isView:
            self._multiViewer = MultiViewer(self.room, self.view, self.viewIdentifier, self.viewArguments, self.dataView, self, autoUpdate=True)
        elif self.source != None:
            if self.sourcePath != None:
                if ':' in self.source:
                    room, source = self.source.split(':') 
                else:
                    room = self.room
                    source = self.source

                if '|' in self.sourcePath:
                    sourcePath, self._subPath = self.sourcePath.split('|')
                else:
                    sourcePath = self.sourcePath
                    self._subPath = None

                if source == "__DOC__":
                    self._listPeer = Viewer(room, self._fillComboBox, sourcePath, raw=True)
                else:
                    self._listPeer = ListPeer(room, self._fillComboBox, sourcePath, source)
        else:
            if self.sourcePath != None:
                if '|' in self.sourcePath:
                    sourcePath, self._subPath = self.sourcePath.split('|')
                else:
                    sourcePath = self.sourcePath
                    self._subPath = None

                self._viewPeer = Viewer(self.room, self._fillComboBox, self.sourcePath)

    # def mousePressEvent(self, event):
    #     QtGui.QComboBox.mousePressEvent(self, event)

    #     if self.isView:
    #         self._multiViewer._updateQuery()

    def _resolve(self, value, **ka):
        self._setItemText(value)
        if self._editor: 
            self._editor._resolve(**ka)
            self._selectOther(None)

    def _selectOther(self, val):
        if self.selectPillow != None and val >= 0:
            val = unicode(self.itemText(val))
            if val in self._translate: val = self._translate[val]
            # print val, isinstance(val, (list, tuple))
            House.get(self.room).throw(self.selectPillow, val)

        if self._editor and self._changed:
            self._editor._fieldChanged()

    def _setItemText(self, val):
        self._changed = False
        self._lastValue = val
        if val:
            val = unicode(val)
            self._lastValue = val # unicode version

            if val in self._translateReverse: val = self._translateReverse[val]
            exists = False
            self.setCurrentIndex(0)
            for i in range(self.count()):
                if val == unicode(self.itemText(i)):
                    self.setCurrentIndex(i)
                    exists = True
            if not exists:
                self.setCurrentIndex(0)
                if self.lineEdit() != None:
                    self.lineEdit().setText(unicode(val))
        else:
            self.setCurrentIndex(0)
            if self.lineEdit() != None:
                self.lineEdit().setText(u"")

        self._changed = True

    def _fillComboBox(self, document):
        self._changed = False

        self._translate = {}
        self._translateReverse = {}
        self.clear()

        if self.source != None and "__DOC__" in self.source:
            if document is not None and self._subPath != None:
                from wallaby.common.pathHelper import PathHelper
                titles = []
                for dct in document:
                    titles.append(PathHelper.getValue(dct, self._subPath))
            else:
                titles = document
        else:
            path = self.sourcePath
            if path == None: path = 'titles'
            titles = document.get(path)

        if titles:
            for i in range(len(titles)):
                value = titles[i]
                if isinstance(value, (list, tuple)):
                    displayValue, value = value
                else:
                    displayValue = value

                self._translate[displayValue] = value
                # if isinstance(value, (unicode, str)):
                self._translateReverse[unicode(value)] = displayValue

                self.insertItem(i, displayValue)
                if value == self._lastValue:
                    self.setCurrentIndex(i)

        self._changed = True

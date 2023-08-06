# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..baseWidget import *
from wallaby.frontends.qt.models.multiViewTableModel import *
from wallaby.pf.peer.actionButtonPeer import *
from imageDelegate import *

class TreeView(QtGui.QTreeView, BaseWidget):
    __metaclass__ = QWallabyMeta

    room    = Meta.property("string")
    dbColumns  = Meta.property("list")
    tab        = Meta.property("string")

    sortable   = Meta.property("list")

    view           = Meta.property("string")
    viewArguments  = Meta.property("dict")
    viewIdentifier = Meta.property("string")
    dataView       = Meta.property("bool")

    doubleClickPillow   = Meta.property("string")
    doubleClickFeathers = Meta.property("string")
    doubleClickTab      = Meta.property("string")

    keyCodePillows     = Meta.property("list")

    multiSelect = Meta.property("bool")

    def __init__(self, parent = None):
        QtGui.QTreeView.__init__(self, parent)
        BaseWidget.__init__(self, QtGui.QTreeView)

        self.setSortingEnabled(False)
        self._sortable = {}
        self._columns = []
        self._labels = []
        self._keyCodePillows = {}

        self._ignoreClick = False

        self.header().setStretchLastSection(True)

        self._popup = None

        self._peer = None
        self._model = None

        self.header().setClickable(True)
        self.header().sectionClicked.connect(self._columnClicked)

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.clicked.connect(self._itemClicked)
        self.doubleClicked.connect(self._itemDoubleClicked)

    def _columnClicked(self, col):
        if col >= len(self._columns):
            return

        header = self.header()

        order = 0

        if self._columns[col] in self._sortable:
            order = self._sortable[self._columns[col]]
            if header.sortIndicatorSection() == col:
                order = (order + 1) % 2
            else:
                order = 0
        else:
            if "__default__" in self._sortable:
                order = (self._sortable["__default__"] + 1) % 2
            else:
                order = 0
            col = -1

        header.setSortIndicator(col, order)

        if col > -1:
            self._sortable[self._columns[col]] = order
        else:
            self._sortable["__default__"] = order

        self.model().sort(col, order)

    def _itemClicked(self, index):
        if self._ignoreClick:
            self._ignoreClick = False
            return

        self.resetSelection()

    def keyPressEvent(self, event):
        QtGui.QTableView.keyPressEvent(self, event)        

        if event.modifiers() & QtCore.Qt.ControlModifier and event.key() in self._keyCodePillows:
            pillow, feathers = self._keyCodePillows[event.key()]
            House.get(self.room).throw(pillow, feathers)
        else:
            self.resetSelection()

    def selectionChanged(self, selected, deselected):
        QtGui.QTableView.selectionChanged(self, selected, deselected)

        if self.multiSelect:
            sel = self.selectionModel().selectedIndexes()
            selection = set() 
            for s in sel:
                selection.add(s.row())

            self.model().doMultiSelect(selection)

    def resetSelection(self):
        sel = self.selectionModel().selectedIndexes()
        if len(sel) == 0:
            self.model().doSelect(None, None)
        else:
            self.model().doSelect(sel[0].row(), self.tab)

    def _itemDoubleClicked(self, index):
        # FIXME
        self._ignoreClick = True

        if self._peer:
            self._peer.buttonClicked()

    def deregister(self, remove=False):
        if self._model: self._model.destroyPeers(remove)
        if self._peer: self._peer.destroy(remove)
        self._peer = None

    def register(self):
        for c in self.sortable:
            self._sortable[c] = 0

        if len(self._sortable) > 0:
            self.header().setSortIndicatorShown(True)

        if self.multiSelect:
            self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self._columns, self._labels = FX.splitList(self.dbColumns, ':')
        self._types, _, self._columns = FX.extractType(self._columns)

        if self.keyCodePillows != None:
            for kca in self.keyCodePillows:
                kca = unicode(kca)
                code, pillow = kca.split(':')
                feathers = None
                if ',' in pillow:
                    feathers = pillow.split(',')
                    pillow = feathers.pop(0)

                code = eval("QtCore.Qt." + code)

                self._keyCodePillows[code] = (pillow, feather)

        col = 0
        for t in self._types:
            if isinstance(t, dict):
                for k, v in t.items():
                    if len(v) > 0 and v[0] == ':':
                        self.setItemDelegateForColumn(col, ImageDelegate())

            col = col + 1

        if self.doubleClickPillow != None:
            self._peer = ActionButtonPeer(self.room, self.doubleClickPillow, self.doubleClickFeathers, tab=self.doubleClickTab)

        self._model = MultiViewTableModel(self, self.dbColumns, roomName=self.room, view=self.view, viewIdentifier=self.viewIdentifier, viewArguments=self.viewArguments, dataView=self.dataView)
        self.setModel(self._model)


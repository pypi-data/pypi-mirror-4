# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..baseWidget import *
from ..logics import *
from wallaby.pf.peer.editor import *

from imageDelegate import *
from comboBoxDelegate import *

class EmbeddedViewTable(QtGui.QTableView, BaseWidget, EnableLogic, EditLogic, TriggeredPillowsLogic):
    __metaclass__ = QWallabyMeta

    room         = Meta.property("string")
    path         = Meta.property("string")
    reverseOrder = Meta.property("bool")
    identifier   = Meta.property("string")
    isList       = Meta.property("bool", default=True)
    dbColumns    = Meta.property("list")
    wrapInList   = Meta.property("bool")
    sizeHints  = Meta.property("dict")

    notSelectableIfDisabled = Meta.property("bool", default=False)

    doubleClickPillow   = Meta.property("string", extended=True)
    doubleClickFeathers = Meta.property("string", extended=True)
    doubleClickTab      = Meta.property("string", extended=True)

    autoResizeCells = Meta.property("bool", extended=True)
    minRowHeight = Meta.property("int", extended=True)
    minColumnWidth = Meta.property("int", extended=True)

    editOnInsert = Meta.property("bool")

    triggers = Meta.property("list", readOnly=True, default=["", "clicked", "double-clicked", "key"])

    def __init__(self, parent = None):
        QtGui.QTableView.__init__(self, parent)
        BaseWidget.__init__(self, QtGui.QTableView)
        EnableLogic.__init__(self)
        EditLogic.__init__(self, Editor, self.getData)
        TriggeredPillowsLogic.__init__(self)

        self.setSortingEnabled(False)

        self.horizontalHeader().setStretchLastSection(True)

        self._popup = None
        self._model = None
        self._actionPeer = None
        self._ignoreClick = False

        self._proxyModel = None
        self._selectedRow = None

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.verticalHeader().sectionMoved.connect(self.reorderRows)
        self.verticalHeader().setMovable(True) 

        self.verticalHeader().sectionClicked.connect(self._itemClicked)

        self.clicked.connect(self._itemClicked)
        self.doubleClicked.connect(self._itemDoubleClicked)

        self._autoColumns = []

        self._imageDelegate = ImageDelegate()
        self._progressDelegate = ProgressDelegate()
        self._comboDelegates = []

    def editCell(self, row, col):
        idx = self._model.createIndex(row, col)
        if self._proxyModel is not None:
            idx = self._proxyModel.mapFromSource(idx)

        print "Set index", QtGui.QTableView.setCurrentIndex(self, idx)
        print "EDIT", QtGui.QTableView.edit(self, idx, QtGui.QTableView.AllEditTriggers, None)  

    def selectRow(self, row):
        if self._proxyModel is not None:
            idx = self._model.createIndex(row, 0)
            idx = self._proxyModel.mapFromSource(idx)
            row = idx.row()   

        QtGui.QTableView.selectRow(self, row)   

    def newData(self):
        if not self.autoResizeCells: return

        self.horizontalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        self.verticalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

        # for c in self._autoColumns:
        #    self.horizontalHeader().setResizeMode(c, QtGui.QHeaderView.ResizeToContents)

        if len(self._autoColumns) > 0:
            self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

    def _resolve(self, value, **ka):
        self._model.resolve(data=value, **ka)

    def getData(self):
        self._model.getData()

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        EditLogic.deregister(self, remove)
        TriggeredPillowsLogic.deregister(self, remove)

        if self._model:
            FXUI.mainWindow.settings().setValue(self._template + "_headerState", self.horizontalHeader().saveState())

        if self._model: self._model.destroyPeers(remove)
        if self._actionPeer: self._actionPeer.destroy(remove)
        self._actionPeer = None

    def reorderRows(self, row, oldIndex, newIndex):
        if self._model != None:
            self._model.reorderRows(row, oldIndex, newIndex)

    def register(self):
        EnableLogic.register(self)
        EditLogic.register(self)
        TriggeredPillowsLogic.register(self)

        if isinstance(self.dbColumns, list) and len(self.dbColumns) > 0 and isinstance(self.dbColumns[0], (str, unicode)):
            columns, labels = FX.splitList(self.dbColumns, ':')
            types, args, columns = FX.extractType(columns, json=False)

            dbColumns = []

            # convert old format
            for i in range(len(columns)):
                dbColumns.append({
                    'path': columns[i],
                    'label': labels[i],
                    'type': types[i],
                    'type-args': args[i]
                })

            self.dbColumns = dbColumns
 

        self._columns = []
        self._labels = []
        self._types = []
        for cfg in self.dbColumns:
            if cfg is None: continue

            self._columns.append(cfg.get('path', None))
            self._labels.append(cfg.get('label', None))
            self._types.append(FX.convertType(cfg.get('type', None)))

        self._autoColumns = []
        self._comboDelegate = []
        col = 0
        for t in self._types:
            hasDelegate = False
            if t is None: 
                col = col + 1
                continue
            if isinstance(t, dict):
                for k, v in t.items():
                    if not hasDelegate and len(v) > 0 and v[0] == ':':
                        self.setItemDelegateForColumn(col, self._imageDelegate)
                        self._autoColumns.append(col)
                        hasDelegate = True
            elif "image" in t:
                self.setItemDelegateForColumn(col, self._imageDelegate)
                self._autoColumns.append(col)
                hasDelegate = True
            elif t == "progress":
                self.setItemDelegateForColumn(col, self._progressDelegate)
            elif t == "comboedit":
                print "set combo delegate"
                self._comboDelegate.append(ComboBoxDelegate(self, col))
                self.setItemDelegateForColumn(col, self._comboDelegate[-1])

            col = col + 1

        from wallaby.frontends.qt.models.embeddedViewTableModel import EmbeddedViewTableModel
        self._model = EmbeddedViewTableModel(self, self.room, self.path, self.dbColumns, conflictCB=self._conflict, isList=self.isList, identifier=self.identifier, reverseOrder=self.reverseOrder, minRowHeight=self.minRowHeight, minColumnWidth=self.minColumnWidth, wrapInList=self.wrapInList, sizeHints=self.sizeHints, editOnInsert=self.editOnInsert)

        if FXUI.mainWindow.options() != None and FXUI.mainWindow.options().app != "inspector":
            self._proxyModel = QtGui.QSortFilterProxyModel(self)
            self._proxyModel.setSourceModel(self._model)
            self._proxyModel.setFilterRegExp(QtCore.QRegExp("^(?!inspector-|itest-)", QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp2))
            # proxyModel.setFilterRegExp(QtCore.QRegExp("^inspector", QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp2))

            # proxyModel.setFilterKeyColumn(0) 
            self.setModel(self._proxyModel)
        else:
            self.setModel(self._model)

        if self.doubleClickPillow != None:
            self._actionPeer = ActionButtonPeer(self.room, self.doubleClickPillow, self.doubleClickFeathers, tab=self.doubleClickTab, translate=True)

        QtCore.QTimer.singleShot(0, self.restoreSettings) 

    def restoreSettings(self):
        headerState = FXUI.mainWindow.settings().value(self._template + "_headerState")
        # if headerState: self.horizontalHeader().restoreState(headerState)

    def _itemDoubleClicked(self, index):
        # FIXME
        self._ignoreClick = True

        self.trigger("double-clicked")
        if self._actionPeer:
            self._actionPeer.buttonClicked(index.row())

    def _itemClicked(self, index):
        if self._ignoreClick:
            self._ignoreClick = False
            # return

        self.resetSelection()
        self.trigger("clicked")

    def setEnabled(self, enabled):
        if self.notSelectableIfDisabled:
            QtGui.QTableView.setEnabled(self, enabled)
            return

        if not enabled:
            self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        else:
            self.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)

    def keyPressEvent(self, event):
        import wallaby.FXUI as FXUI 
        if self.trigger("key", FXUI.key_event_to_name(event)):
            event.accept()
        else:
            event.ignore()
            QtGui.QTableView.keyPressEvent(self, event)        

            if self.state() != QtGui.QAbstractItemView.EditingState:
                self.resetSelection()

    # def selectionChanged(self, selected, deselected):
    #     QtGui.QTableView.selectionChanged(self, selected, deselected)
    #     sel = self.selectionModel().selectedIndexes()
    #     if len(sel) == 0:
    #         self._model.doSelect(None)
    #     else:
    #         self._model.doSelect(sel[0].row())

    def resetSelection(self):
        sel = self.selectionModel().selectedIndexes()
        if len(sel) == 0:
            self._model.doSelect(None)
        else:
            if self._proxyModel != None:
                sel = self._proxyModel.mapToSource(sel[0])
            else:
                sel = sel[0]

            self._selectedRow = sel.row()

            self._model.doSelect(self._selectedRow)
            self.scrollTo(sel)

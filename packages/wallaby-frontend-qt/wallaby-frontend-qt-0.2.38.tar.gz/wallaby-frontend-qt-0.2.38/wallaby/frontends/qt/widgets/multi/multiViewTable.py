# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from wallaby.common.sets import *
from ..baseWidget import *
from ..logics import *
from wallaby.pf.peer.actionButtonPeer import *
from wallaby.pf.peer.multiViewer import *
from imageDelegate import *

class MultiViewTable(QtGui.QTableView, BaseWidget, EnableLogic, ContextMenuLogic, TriggeredPillowsLogic):
    __metaclass__ = QWallabyMeta

    room       = Meta.property("string")
    # Delete if all apps are converted
    dbColumns  = Meta.property("list")
    tab        = Meta.property("string")

    sortable   = Meta.property("list")
    sizeHints  = Meta.property("dict")

    orderPath = Meta.property("string")

    queryDocID    = Meta.property("string")

    view           = Meta.property("string")
    viewArguments  = Meta.property("dict")
    viewIdentifier = Meta.property("string")
    dataView       = Meta.property("bool")

    idVisible = Meta.property("bool")

    doubleClickPillow   = Meta.property("string")
    doubleClickFeathers = Meta.property("string")
    doubleClickTab      = Meta.property("string")

    keyCodePillows      = Meta.property("list")

    autoResizeCells = Meta.property("bool")
    minRowHeight = Meta.property("int")
    minColumnWidth = Meta.property("int")

    multiSelect = Meta.property("bool")

    triggers = Meta.property("list", readOnly=True, default=["", "clicked", "double-clicked", "key"])

    def getMenuEntries(self): return ContextMenuLogic.getMenuEntries(self)

    def overlayLabel(self):
        rooms = OrderedSet() 
        rooms.add(self.room)

        if self.room == None:
            return [rooms]

        if self.viewIdentifier != self.room and self.viewIdentifier != None:
            rooms.add(self.viewIdentifier.upper())

        rooms |= House.pillowRooms(self.room, MultiViewer.Out.Select, None)

        if self.doubleClickPillow != None:
            rooms |= House.pillowRooms(self.room, self.doubleClickPillow, self.doubleClickFeathers)

        for room, pillow, feathers in self._keyCodePillows.values():
            rooms |= House.pillowRooms(room, pillow, feathers)
            
        if self.view != None:
            return (rooms, self.view)
        else:
            return (rooms, "external query")

    def __init__(self, parent = None):
        QtGui.QTableView.__init__(self, parent)
        BaseWidget.__init__(self, QtGui.QTableView)
        EnableLogic.__init__(self)
        TriggeredPillowsLogic.__init__(self)

        self.setSortingEnabled(False)
        self._sortable = {}
        self._sortField = {}
        self._columns = []
        self._labels = []
        self._autoColumns = []
        self._keyCodePillows = {}

        self._ignoreClick = False

        self.horizontalHeader().setStretchLastSection(True)

        self._popup = None

        self._actionPeer = None
        self._model = None

        self.horizontalHeader().setClickable(True)
        self.horizontalHeader().sectionClicked.connect(self._columnClicked)

        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.verticalHeader().setClickable(True)
        self.verticalHeader().sectionClicked.connect(self._itemClicked)

        self.verticalHeader().sectionMoved.connect(self.reorderRows)

        self.clicked.connect(self._itemClicked)
        self.doubleClicked.connect(self._itemDoubleClicked)

        self._imageDelegate = ImageDelegate()
        self._progressDelegate = ProgressDelegate()

#         self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
#         self.viewport().setAcceptDrops(True)
#         self.setDropIndicatorShown(False)

    def reorderRows(self, row, oldIndex, newIndex):
        if self.model() != None:
            self.model().reorderRows(row, oldIndex, newIndex)

    def _columnClicked(self, col):
        if col-1 >= len(self._columns) or len(self._sortable) == 0:
            return

        column = self._columns[col-1]
        header = self.horizontalHeader()

        if column not in self._sortable:
            header.setSortIndicator(-1, 0)
            return False
        order = 0

        order = self._sortable[self._columns[col-1]]
        if header.sortIndicatorSection() == col:
            order = (order + 1) % 2
        else:
            order = 0

        header.setSortIndicator(col, order)

        self._sortable[column] = order
        self.model().sort(self._sortField[column], order)

    def _itemClicked(self, index):
        if self._ignoreClick:
            self._ignoreClick = False
            # return

        self.resetSelection()
        self.trigger("clicked")

    def keyPressEvent(self, event):
        accept = False

        import wallaby.FXUI as FXUI 
        if self.trigger("key", FXUI.key_event_to_name(event)):
            accept = True
 
        if event.modifiers() & QtCore.Qt.ControlModifier and event.key() in self._keyCodePillows:
            room, pillow, feathers = self._keyCodePillows[event.key()]
            House.get(room).throw(pillow, feathers)
            accept = True

        if accept:
            event.accept()
            QtGui.QTableView.keyPressEvent(self, event)        
        else:
            event.ignore()
            QtGui.QTableView.keyPressEvent(self, event)        
            self.resetSelection()

    def selectionChanged(self, selected, deselected):
        QtGui.QTableView.selectionChanged(self, selected, deselected)

        if self.multiSelect:
            sel = self.selectionModel().selectedIndexes()
            selection = set() 
            for s in sel:
                selection.add(s.row())

            self.model().doMultiSelect(selection)

    def initialData(self):
        if not self.autoResizeCells: return
        print "Initial"

        self.horizontalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        self.verticalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

        # for c in self._autoColumns:
        #    self.horizontalHeader().setResizeMode(c, QtGui.QHeaderView.ResizeToContents)

        if len(self._autoColumns) > 0:
            self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

    def clearSelection(self):
        self.selectionModel().clear()
        self.model().doSelect(None, None)

    def resetSelection(self):
        # FIXME
        # if self.autoResizeCells: self.initialData()
        sel = self.selectionModel().selectedIndexes()
        if len(sel) == 0:
            self.model().doSelect(None, None)
            # Ignore null selection
            # pass
        else:
            self.model().doSelect(sel[0].row(), self.tab)

    def _itemDoubleClicked(self, index):
        # FIXME
        self._ignoreClick = True

        self.trigger("double-clicked")

        if self._actionPeer:
            self._actionPeer.buttonClicked()

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        TriggeredPillowsLogic.deregister(self, remove)

        FXUI.mainWindow.settings().setValue(self._template + "_headerState", self.horizontalHeader().saveState())

        if self._model: self._model.destroyPeers(remove)
        if self._actionPeer: self._actionPeer.destroy(remove)

        self._actionPeer = None

    def register(self):
        EnableLogic.register(self)
        TriggeredPillowsLogic.register(self)

        self._sortable = {}
        self._sortField = {"__default__": "__default__"}

        sortable = []


        converted = False
        for c in self.sortable:
            if c is None: 
                sortable.append(None)
                continue
                
            if isinstance(c, (unicode, str)):
                if ':' in c:
                    c, field = c.split(':')
                else:
                    field = c

                sortable.append({'sortPath': field, 'path': c})
                converted = True
            else:
                sortable.append(c)

        if converted: self.sortable = sortable

        for c in self.sortable:
            if c is None: continue

            field = c.get('sortPath', None)
            c = c.get('path', None)
               
            self._sortable[c] = 0
            self._sortField[c] = field

        if len(self._sortable) > 0:
            self.horizontalHeader().setSortIndicatorShown(True)
        else:
            self.horizontalHeader().setSortIndicatorShown(False)

        if self.multiSelect:
            self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        else:
            self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

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

        if self.orderPath != None:
            self.verticalHeader().setMovable(True) 

        if self.keyCodePillows != None:
            for kca in self.keyCodePillows:
                kca = unicode(kca)
                lst = kca.split(':')
                code = lst.pop(0)
                if len(lst) >= 2:
                    room = lst.pop(0)
                else:
                    room = self.room

                pillow = lst.pop(0)

                feathers = None
                if ',' in pillow:
                    feathers = pillow.split(',')
                    pillow = feathers.pop(0)

                code = eval("QtCore.Qt." + code)

                self._keyCodePillows[code] = (room, pillow, feathers)


        self._autoColumns = []
        col = 0
        for t in self._types:
            hasDelegate = False
            if isinstance(t, dict):
                for k, v in t.items():
                    if not hasDelegate and len(v) > 0 and v[0] == ':':
                        self.setItemDelegateForColumn(col+1, self._imageDelegate)
                        self._autoColumns.append(col+1)
                        hasDelegate = True
            elif t == "progress":
                self.setItemDelegateForColumn(col+1, self._progressDelegate)
            elif t == "image":
                self.setItemDelegateForColumn(col+1, self._imageDelegate)
                self._autoColumns.append(col+1)
                hasDelegate = True

            col = col + 1

        if self.doubleClickPillow != None:
            self._actionPeer = ActionButtonPeer(self.room, self.doubleClickPillow, self.doubleClickFeathers, tab=self.doubleClickTab)

        from wallaby.frontends.qt.models.multiViewTableModel import MultiViewTableModel
        self._model = MultiViewTableModel(self, self.dbColumns, room=self.room, view=self.view, viewIdentifier=self.viewIdentifier, viewArguments=self.viewArguments, dataView=self.dataView, orderPath=self.orderPath, minRowHeight=self.minRowHeight, minColumnWidth=self.minColumnWidth, queryDocID=self.queryDocID, sizeHints=self.sizeHints)
        self.setModel(self._model)

        if self.idVisible:
            self.setColumnHidden(0, False)
        else:
            self.setColumnHidden(0, True)



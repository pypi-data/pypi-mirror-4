# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX
import wallaby.FXUI as FXUI
from functools import partial
from wallaby.qt_combat import *


from wallaby.pf.peer.incrementalMultiViewer import *
from twisted.internet import defer

class MultiViewTableModel(QtCore.QAbstractTableModel):
    def __init__(self, widget, cols=None, *args, **ka):
        QtCore.QAbstractTableModel.__init__(self, None)

        self._widget = widget

        self._peer = IncrementalMultiViewer(*args, delegate=self, **ka)

        self._updateChangedDeferred = None
        self._maxRow = self._minRow = -1

        self._columns  = []
        self._types    = []
        self._typeArgs = []
        self._labels   = []
        self._cache    = []
        self._parent   = QtCore.QModelIndex()

        if cols == None: cols = []

        self._minRowHeight = 0
        self._minColumnWidth = 0

        self._loading = 0

        self._sizeHints = {}

        if 'minRowHeight' in ka: self._minRowHeight = ka['minRowHeight']
        if 'minColumnWidth' in ka: self._minColumnWidth = ka['minColumnWidth']
        if 'sizeHints' in ka: self._sizeHints = ka['sizeHints']

        if self._minRowHeight == None: self._minRowHeight = 0
        if self._minColumnWidth == None: self._minColumnWidth = 0
        if self._sizeHints == None: self._sizeHints = {}

        if isinstance(cols, list) and len(cols) > 0 and isinstance(cols[0], dict):
            cols.insert(0, {'path':'id'})
            self._columns = []
            self._labels = []
            self._types = []
            self._typeArgs = []
            for cfg in cols:
                if cfg is None: continue
                self._columns.append(cfg.get('path', None))
                self._labels.append(cfg.get('label', None))
                self._types.append(FX.convertType(cfg.get('type', None)))
                self._typeArgs.append(cfg.get('type-args', None))
        else: 
            cols.insert(0, 'id')
            self._columns, self._labels = FX.splitList(cols, ':')
            self._types, self._typeArgs, self._columns = FX.extractType(self._columns)

    def initialData(self):
        if self._widget: self._widget.initialData()

    def flags(self, index):
        defaultFlags = QtCore.QAbstractTableModel.flags(self, index)

        if index.isValid():
            return QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | defaultFlags
        else:
            return QtCore.Qt.ItemIsDropEnabled | defaultFlags

    # def supportedDropActions(self):
    #     return QtCore.Qt.MoveAction
    # 
    # def supportedDragActions(self):
    #     return QtCore.Qt.MoveAction

    def destroyPeers(self, remove=False):
        self._peer.destroy(remove)
        self.__peer = None

    def doMultiSelect(self, *args, **ka):
        if not self._peer: return

        self._peer.doMultiSelect(*args, **ka)

    def selectRow(self, row):
        self._widget.selectRow(row)

    def doSelect(self, idx, tab):
        if not self._peer: return

        self._peer.doSelect(idx, tab)

    # def insertRows(self, row, count, parent):
    #     print "insertRows", row, count
    #     return True

    # def removeRows(self, row, count, parent):
    #     print "removeRows", row, count
    #     return True

    def sort(self, field, order):
        if not self._peer: return
        self._peer.sort(field, order)

    def hasChildren(self, index):
        return False

    def clearSelection(self):
        self._widget.clearSelection()

    def beginInsertCB(self, f, cnt):
        self.beginInsertRows(self._parent, f, f + cnt - 1)

        i = f
        for j in range(cnt):
            cols = []
            for k in range(len(self._columns)): cols.append({'cached': False, 'value': None, 'loading': False})

            self._cache.insert(i, {'cache': cols, 'loading': False})
            i = i + 1

    def resetSelectionCB(self):
        if self._widget: self._widget.resetSelection()

    def endInsertCB(self, f, cnt):
        self.emit(QtCore.SIGNAL('rowsInserted'), self._parent, f, cnt - 1)
        self.endInsertRows()

    def beginDeleteCB(self, f, t):
        self.beginRemoveRows(self._parent, f, t-1)

        for i in range(f, t):
            if f < len(self._cache):
                self._cache.pop(f)
            else:
                print "Try to remove out of bounds!", f, "of", len(self._cache) 

    def endDeleteCB(self, f, t):
        self.emit(QtCore.SIGNAL('rowsRemoved'), self._parent, f, t-1)
        self.endRemoveRows()

    def updateCB(self, row):
        if row < len(self._cache):
            self._cache[row]['loading'] = False
            for i in range(len(self._cache[row]['cache'])): self._cache[row]['cache'][i]['cached'] = False
            self.dataChanged.emit(self.index(row, 0), self.index(row, len(self._columns)-1))
                
    def parent(self, index):
        return self._parent

    def index(self, row, col, parent=QtCore.QModelIndex()):
        return self.createIndex(row, col)

    def rowCount(self, parent): 
        return len(self._cache)

    def columnCount(self, parent): 
        return len(self._columns)

    def getID(self, row):
        if len(self._rows) <= row:
            return "N/A"
        else:
            return self._rows[row].id

    def _empty(self):
        return None

    def reorderRows(self, row, oldIndex, newIndex):
        i1 = newIndex
        i2 = newIndex+1

        if newIndex < oldIndex:
            i1 -= 1
            i2 -= 1

        self._peer.reorder(row, i1, i2)

    # def setData(self, index, value, role=QtCore.Qt.EditRole):
    #     print "Setting Data", value.toString(), "at", index.row(), index.column()
    #     return True

    def data(self, index, role=QtCore.Qt.DisplayRole): 
        if not index.isValid(): return self._empty()

        row = index.row()
        col = index.column()

        if role == QtCore.Qt.SizeHintRole:
            if self._columns[col] in self._sizeHints and isinstance(self._sizeHints[self._columns[col]], dict):
                hint = self._sizeHints[self._columns[col]]
                w = self._minColumnWidth
                h = self._minRowHeight
                if 'width' in hint and hint['width'] is not None: w = int(hint['width'])
                if 'height' in hint and hint['height'] is not None: h = int(hint['height'])
                # print w, h, col
                return QtCore.QSize(w, h)
            else:
                size = QtCore.QSize(self._minColumnWidth, self._minRowHeight)

            if len(self._columns) <= col or self.rowCount(self.parent) <= row or not self._cache[row]['cache'][col]['cached']:
                return size

            # if row == 0:
            #     print "Size", row, col, size.width(), size.height()

            val = self._cache[row]['cache'][col]['value']

            if isinstance(val, QtGui.QPixmap):
                size.setWidth(min(100, max(val.width()+1, size.width())))
                size.setHeight(min(100, max(val.height(), size.height())))

            elif isinstance(val, (list, tuple)):
                w = h = 0
                for e in val:
                    if isinstance(e, QtGui.QPixmap):
                        w += e.width()
                        if h < e.height(): h = e.height()

                size.setWidth(max(w+1, size.width()))
                size.setHeight(max(h, size.height()))
            else:
                return self._empty() 
            return size
 
        if role != QtCore.Qt.DisplayRole or self.rowCount(self._parent) <= row or len(self._columns) <= col: return self._empty()

        # if self._cache[row]['loading']:
        #     if col == 0:
        #         return "Loading..."
        #     else:
        #         return ""

        if self._cache[row]['cache'][col]['cached']:
            val = self._cache[row]['cache'][col]['value']
            if val == None:
                return '-'
            else:
                return val

        if self._cache[row]['cache'][col]['loading']:
            if col == 1:
                return "Loading..."
            else:
                return ""

        if not self._peer: return '-'

        self._cache[row]['cache'][col]['loading'] = True

        self._cache[row]['loading'] = True
        self._loading += 1
        d = self._peer.deferredGetValue(row, self._columns[col])
        d.addCallback(partial(self._updateField, row, col))

        if 'value' in self._cache[row]['cache'][col]:
            val = self._cache[row]['cache'][col]['value']
            if val is None: return ""
            else: return val
        else:
            if col == 1:
                return "Loading..."
            else:
                return ""

    def _updateField(self, row, col, val):
        self._loading -= 1
        if row >= len(self._cache): return

        self._cache[row]['cache'][col]['loading'] = False

        # if isinstance(val, QtGui.QPixmap):
        #     print val, val.width(), val.height()

        if val != None and self._types[col] == "image" and not isinstance(val, QtGui.QPixmap):
            if self._typeArgs[col] and len(self._typeArgs[col]) > 0:
                d = self._peer.getImage(row, self._typeArgs[col], documentID=val)
            else:
                d = self._peer.getImage(row, val)
            d.addCallback(partial(self._updateField, row, col))

        val = FXUI.renderType(val, self._types[col], self._typeArgs[col]) 

        self._cache[row]['loading'] = False
        self._cache[row]['cache'][col]['cached'] = True
        self._cache[row]['cache'][col]['value']  = val

        if self._minRow == -1 or row < self._minRow: self._minRow = row
        if self._maxRow == -1 or row > self._maxRow: self._maxRow = row

        if self._updateChangedDeferred is not None:
            try:
                self._updateChangedDeferred.cancel()
            except: pass

        from twisted.internet import reactor
        self._updateChangedDeferred = reactor.callLater(1.0, self._updateChanged)
        # self.dataChanged.emit(self.index(row, col), self.index(row, col))
        # if self._loading == 0: self.layoutChanged.emit()
        return val

    def _updateChanged(self):
        self._updateChangedDeferred = None
        self.dataChanged.emit(self.index(self._minRow, 0), self.index(self._maxRow, len(self._columns)-1))
        self._maxRow = self._minRow = -1

    def headerData(self, col, orientation, role):
        if not QtCore: return
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col >= len(self._labels):
                return None

            return self._labels[col]

        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return '%03d' % (col+1)

        return None


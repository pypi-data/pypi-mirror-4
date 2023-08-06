#!/usr/bin/env python
# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

from functools import partial

from wallaby.qt_combat import *

from wallaby.pf.peer.multiViewer import *

class TreeViewTableModel(QtCore.QAbstractItemModel):
    def __init__(self, widget, cols=['_id'], *args, **ka):
        QtCore.QAbstractTableModel.__init__(self, None)

        self._widget = widget

        self._peer = MultiViewer(*args, delegate=self, **ka)

        self._columns  = []
        self._types    = []
        self._typeArgs = []
        self._labels   = []
        self._cache    = []
        self._root     = QtCore.QModelIndex()

        self._columns, self._labels = FX.splitList(cols, ':')
        self._types, self._typeArgs, self._columns = FX.extractType(self._columns)

    def doMultiSelect(self, *args, **ka):
        # self._peer.doMultiSelect(*args, **ka)
        pass

    def doSelect(self, idx, tab):
        # self._peer.doSelect(idx, tab)
        pass

    def sort(self, col, order):
        # if not self._peer or col >= len(self._columns): return

        # if col == -1:
        #     self._peer.sort('__default__', order)
        # else:
        #     self._peer.sort(self._columns[col], order)
        pass

    def hasChildren(self, index):
        return False

    def beginInsertCB(self, f, cnt):
        self.beginInsertRows(self._parent, f, f + cnt - 1)

        i = f
        for j in range(cnt):
            cols = []
            for k in range(len(self._columns)): cols.append({'cached': False, 'value': None})

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
        if FX.PyQt4:
            return QtCore.QVariant()
        else:
            return None

    def data(self, index, role): 
        if not index.isValid(): return self._empty()

        row = index.row()
        col = index.column()

        if role == QtCore.Qt.SizeHintRole:
            if len(self._columns) <= col or self.rowCount(self.parent) <= row or not self._cache[row]['cache'][col]['cached']:
                return self._empty()

            val = self._cache[row]['cache'][col]['value']

            if isinstance(val, QtGui.QPixmap):
                return val.size()
            else:
                return None
 
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

        self._cache[row]['loading'] = True
        d = self._peer.deferredGetValue(row, self._columns[col])
        d.addCallback(partial(self._updateField, row, col))

        if col == 0:
            return "Loading..."
        else:
            return ""

    def _updateField(self, row, col, val):
        if row >= len(self._cache): return

        val = FX.renderType(val, self._types[col], self._typeArgs[col]) 

        self._cache[row]['loading'] = False
        self._cache[row]['cache'][col]['cached'] = True
        self._cache[row]['cache'][col]['value']  = val

        self.dataChanged.emit(self.index(row, col), self.index(row, col))
        return val

    def headerData(self, col, orientation, role):
        if not QtCore: return
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col >= len(self._labels):
                if FX.PyQt4:
                    return QtCore.QVariant()
                else:
                    return None

            if FX.PyQt4:
                return QtCore.QVariant(self._labels[col])
            else:
                return unicode(self._labels[col])

        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            if FX.PyQt4:
                return QtCore.QVariant('%03d' % (col+1))
            else:
                return unicode('%03d' % (col+1))

        if FX.PyQt4:
            return QtCore.QVariant()
        else:
            return None


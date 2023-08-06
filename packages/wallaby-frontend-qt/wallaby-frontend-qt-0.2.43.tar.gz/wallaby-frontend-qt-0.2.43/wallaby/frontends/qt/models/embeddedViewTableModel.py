#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX
import wallaby.FXUI as FXUI
from functools import partial

from wallaby.qt_combat import *

from wallaby.common.pathHelper import PathHelper
from wallaby.pf.peer.embeddedViewer import *

class EmbeddedViewTableModel(QtCore.QAbstractTableModel):
    def __init__(self, widget, room, path, cols=['_id'], parent=None, conflictCB=None, isList=True, identifier=None, reverseOrder=False, minRowHeight=None, minColumnWidth=None, wrapInList=False, sizeHints=None, editOnInsert=False, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)

        self._peer   = EmbeddedViewer(room, path, delegate=self, conflictCB=conflictCB, isList=isList, wrapInList=wrapInList, identifier=identifier, editOnInsert=editOnInsert)
        self._widget = widget

        self._reverseOrder = reverseOrder

        self._imageCache = {}

        self._minRowHeight = 0
        self._minColumnWidth = 0
        self._sizeHints = {}

        if minRowHeight != None: self._minRowHeight = int(float(minRowHeight))
        if minColumnWidth != None: self._minColumnWidth = int(float(minColumnWidth))
        if sizeHints != None: self._sizeHints = sizeHints

        self._isList   = isList
        self._wrapInList = wrapInList
        self._columns  = []
        self._labels   = []
        self._types    = []
        self._typeArgs = []
        self._data     = self._emptyData()
        self._parent   = QtCore.QModelIndex()
        self._keys = None
        self._rows = None

        self._length = 0
           
        if isinstance(cols, list) and len(cols) > 0 and isinstance(cols[0], dict):
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
            self._columns, self._labels = FX.splitList(cols, ':')
            self._types, self._typeArgs, self._columns = FX.extractType(self._columns)
        self._path = path

    def _emptyData(self):
        if self._isList:
            return []
        else:
            return {}
            

    def resolve(self, **ka):
        if self._peer: self._peer.resolve(**ka)

    def getData(self):
        return self._data

    def destroyPeers(self, remove=False):
        if self._peer != None:
            self._peer.destroy(remove)

        self._peer = None

    def doSelect(self, row):
        self._peer.select(self.getKey(row))

    def editRow(self, key):
        row = self.getRow(key)
        if row != None:
            for col in range(len(self._types)):
                if self._types[col] in ("dictedit", "listedit", "autoedit", "stringedit", "doubleedit", "numberedit", "currencyedit", "comboedit"):
                    self._widget.editCell(row, col)
                    return 

    def selectRow(self, key):
        row = self.getRow(key)
        if row != None:
            self._widget.selectRow(row)

        self._widget.resetSelection()

    def beginInsertCB(self, idx):
        self.beginInsertRows(self._parent, idx, idx)

    def resetSelectionCB(self):
        if self._widget: self._widget.resetSelection()

    def endInsertCB(self, idx):
        if not self._isList:
            self._keys.insert(idx, "__new__")
            self._mapRows()

        self.emit(QtCore.SIGNAL('rowsInserted'), self._parent, idx, idx)
        self.endInsertRows()

    def beginDeleteCB(self, idx):
        self.beginRemoveRows(self._parent, idx, idx)

    def endDeleteCB(self, idx):
        if not self._isList:
            del self._keys[idx]
            self._mapRows()

        self.emit(QtCore.SIGNAL('rowsRemoved'), self._parent, idx, idx)
        self.endRemoveRows()

    def changedCB(self):
        idx = self._widget.selectedIndexes()

        # clear cache
        self._imageCache = {}

        if len(idx) > 1:
            self.dataChanged.emit(idx[0], idx[1])
        elif len(idx) > 0:
            self.dataChanged.emit(idx[0], idx[0])

    def reorderRows(self, row, oldIndex, newIndex):
        self.beginRemoveRows(self._parent, oldIndex, oldIndex)
        item = self._data.pop(oldIndex)
        self.endRemoveRows()

        self.beginInsertRows(self._parent, newIndex, newIndex)
        self._data.insert(newIndex, item)
        self.endInsertRows()

        self._peer.dataChanged(newIndex)

    def dataCB(self, data):
        # import traceback
        # traceback.print_stack()
        if data == None:
            data = self._emptyData()

        cnt = self.rowCount(self._parent)

        self.beginRemoveRows(self._parent, 0, cnt-1)
        self._data = self._emptyData()
        self._imageCache = {}

        self.emit(QtCore.SIGNAL('rowsRemoved'), self._parent, 0, cnt-1)
        self.endRemoveRows()

        self._length = len(data)

        if self._length > 0:
            self.beginInsertRows(self._parent, 0, self._length-1)
            self._data = data

            if not self._isList:
                self._keys = sorted(self._data.keys())
                self._mapRows()

                self.emit(QtCore.SIGNAL('rowsInserted'), self._parent, 0, self._length-1)
            else:
                self.emit(QtCore.SIGNAL('rowsInserted'), self._parent, 0, self._length-1)

            self.endInsertRows()
        else:
            self._keys = []

        self._widget.newData()

    def _mapRows(self):
        i = 0
        self._rows = {}
        for k in self._keys:
            self._rows[k] = i
            i += 1
 

    def _splitList(self, lst, sep):
        firstList = []
        secondList = []

        for e in lst:
            t = e.split(sep)
            first = t[0]
            if len(t) > 1:
                second = t[1]
            else:
                second = first

            firstList.append(first)
            secondList.append(second)

        return firstList, secondList

    def hasChildren(self, index):
        return False

    def parent(self, index):
        return self._parent

    def index(self, row, col, parent=QtCore.QModelIndex()):
        return self.createIndex(row, col)

    def rowCount(self, parent): 
        if self._isList:
            return self._length
        else:
            if self._keys == None:
                return 0
            else:
                return len(self._keys)

    def columnCount(self, parent): 
        return len(self._columns)

    def flags(self, index):
        col = index.column()
        flags = QtCore.QAbstractTableModel.flags(self, index)

        if col < 0 or col >= len(self._types): return flags

        if self._types[col] in ("dictedit", "listedit", "autoedit", "stringedit", "doubleedit", "numberedit", "currencyedit", "comboedit"):
            flags |= QtCore.Qt.ItemIsEditable

        return flags

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            col = index.column()
            row = index.row()

            if self.rowCount(self._parent) <= row: return False

            key = self.getKey(row)

            oldVal = None 

            if self._columns[col] == '*':
                if (self._isList and key < len(self._data)) or key in self._data:
                    oldVal = self._data[key]
                else:
                    val = u""
            elif self._columns[col] == '__key__':
                oldVal = key
            else:
                if self._isList:
                    if key < len(self._data): oldVal = PathHelper.getValue(self._data[key], self._columns[col])
                else:
                    if key in self._data: oldVal = PathHelper.getValue(self._data[key], self._columns[col])

            vtype = self._types[col]

            if vtype not in ("autoedit", "dictedit", "listedit") and self._columns[col] == "*" and isinstance(oldVal, (dict, list, tuple)):
                return False

            if vtype == "autoedit":
                if isinstance(oldVal, (float, int)):
                    vtype = "doubleedit"
                elif isinstance(oldVal, bool):
                    vtype = "booledit"
                else:
                    if isinstance(value, (str, unicode)):
                        import re
                        if value == "true" or value == "false":
                            vtype = "booledit"
                        elif re.match(r"^\d+\.?\d*$", value):
                            vtype = "doubleedit"
                        elif re.match(r"^\[", value):
                            vtype = "stringedit"
                            if oldVal is None or not isinstance(oldVal, list): oldVal = []
                        elif re.match(r"^\{", value):
                            vtype = "stringedit"
                            if oldVal is None or not isinstance(oldVal, dict): oldVal = []
                        else:
                            vtype = "stringedit"
                    else:
                        vtype = "stringedit"
            elif vtype == "dictedit":
                vtype = "stringedit"
                if oldVal is None or not isinstance(oldVal, dict): oldVal = {}
            elif vtype == "listedit":
                vtype = "stringedit"
                if oldVal is None or not isinstance(oldVal, list): oldVal = []

            if vtype == "stringedit":
                val = unicode(value)

                if isinstance(oldVal, (list, dict)):
                    import json
                    try:
                        value = json.loads(u'{"value":' + val + u'}')
                        val = value['value']

                    except Exception as e:
                        if isinstance(oldVal, list): val = []
                        elif isinstance(oldVal, dict): val = {}

                if self._columns[col] == '*':
                    self._data[key] = val
                elif not self._isList and self._columns[col] == '__key__':
                    if key in self._data:
                        self._data[val] = self._data[key]
                        del self._data[key]

                    del self._rows[self._keys[row]]
                    self._keys[row] = val
                    self._rows[val] = row
                    self._peer.select(val)
                else:
                    if self._data[key] == None or not isinstance(self._data[key], dict): 
                        self._data[key] = {}

                    PathHelper.setValue(self._data[key], self._columns[col], val)

            elif vtype in ("doubleedit", "numberedit", "currencyedit"):
                val = 0
                if isinstance(value, (unicode, str)):
                    try:
                        val = float(value)
                    except: pass
                elif isinstance(value, (float, int, bool)):
                    val = value

                if self._columns[col] == '*':
                    self._data[key] = val
                elif not self._isList and self._columns[col] == '__key__':
                    self._data[val] = self._data[key]
                    del self._data[key]
                    del self._rows[self._keys[row]]
                    self._keys[row] = val
                    self._rows[val] = row
                    self._peer.select(val)
                else:
                    PathHelper.setValue(self._data[key], self._columns[col], val)
            elif vtype in ("booledit"):
                val = False
                if isinstance(value, (unicode, str)):
                    try:
                        val = bool(value)
                    except: pass
                elif isinstance(value, (bool)):
                    val = value

                if self._columns[col] == '*':
                    self._data[key] = val
                elif not self._isList and self._columns[col] == '__key__':
                    self._data[val] = self._data[key]
                    del self._data[key]
                    del self._rows[self._keys[row]]
                    self._keys[row] = val
                    self._rows[val] = row
                    self._peer.select(val)
                else:
                    PathHelper.setValue(self._data[key], self._columns[col], val)
 

            if vtype in ("stringedit", "doubleedit", "numberedit", "currencyedit", "booledit"):
                self.dataChanged.emit(index, index)
                self._peer.fieldChanged(key, self._columns[col])
                return True

        return False

    def getRow(self, key):
        if self._isList:
            if isinstance(key, (unicode, str)):
                return None
            else:
                return key
        else:
            if self._rows is not None and key not in self._rows:
                return len(self._rows)

            return self._rows[key] 
            
    def getKey(self, row):
        if row == None: return None

        if self._isList:
            return row
        else:
            if row > self._keys:
                return None

            return self._keys[row]

    def data(self, index, role): 
        if not index.isValid(): 
            return None
        elif role != QtCore.Qt.EditRole and role != QtCore.Qt.DisplayRole and role != QtCore.Qt.SizeHintRole:  
            return None

        row = index.row()
        if self.rowCount(self._parent) <= row: return None

        col = index.column()
        if len(self._columns) <= col: return None
 

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

            # if isinstance(val, QtGui.QPixmap):
            #     size.setWidth(max(val.width()+1, size.width()))
            #     size.setHeight(max(val.height(), size.height()))
            return size

        key = self.getKey(row)

        path = self._columns[col]
        type = self._types[col]
        typeArg = self._typeArgs[col]

        pathes = []
        types = []
        typeArgs = []
        
        if path != None and '|' in path:
            pathes = path.split('|')

            if type != None and '|' in type:
                types = type.split('|')
            else:
                for p in pathes: types.append(type)

            if typeArg != None and '|' in typeArg:
                typeArgs = typeArg.split('|')
            else:
                for p in pathes: typeArgs.append(typeArg)

            type = types[-1]
            for i in range(len(types), len(pathes)):
                types.append(type)

            typeArg = typeArgs[-1]
            for i in range(len(typeArgs), len(pathes)):
                typeArgs.append(typeArg)
        else:
            pathes = [path] 
            types = [type]
            typeArgs = [typeArg]

        i = 0
        for i in range(len(pathes)):
            path = pathes[i]
            type = types[i]
            typeArg = typeArgs[i]

            if path == '*':
                if (self._isList and key < len(self._data)) or key in self._data:
                    val = self._data[key]
                else:
                    val = u""
            elif path == '__key__':
                val = key
            else:
                val = PathHelper.getValue(self._data[key], path)
                # print "get", key, self._data[key], self._columns[col], val

            if type == "imagelist":
                if not isinstance(val, list):
                    continue

                images = []

                for dct in val:
                    if isinstance(dct, (unicode, str)):
                        images.append(dct)
                    elif isinstance(dct, dict):
                        if typeArg in dct:
                            images.append(dct[typeArg])
                    elif isinstance(dct, list):
                        if typeArg != None and int(typeArg) < len(dct):
                            images.append(dct[int(typeArg)])

                if str(images) in self._imageCache:
                    return self._imageCache[str(images)]

                dList = []

                for img in images:
                    dList.append(self._peer.getImage(img))

                d = defer.DeferredList(dList)
                d.addCallback(partial(self._updateField, row, col, str(images)))
                return  [QtGui.QPixmap()]

            if type == "image":
                if val in self._imageCache:
                    val = self._imageCache[val]
                else:
                    if not self._peer.hasImage(val):
                        val = None
                        continue

                    d = self._peer.getImage(val)
                    d.addCallback(partial(self._updateField, row, col, val))
                    val = QtGui.QPixmap()
            else:
                val = FXUI.renderType(val, type, typeArg, role == QtCore.Qt.EditRole) 

            if val != None:
                return val
        return val

    def _updateField(self, row, col, path, val):
        if isinstance(val, list):
            lst = []
            for success, value in val:
                if success:
                    lst.append(value)
        else:
            lst = [val]

        pixmaps = []

        for val in lst:
            img = QtGui.QImage.fromData(val)
            if img.width() > 0:
                origPath = self._columns[col]
                h = 128
                w = 128
                if origPath in self._sizeHints:
                    hint = self._sizeHints[origPath]
                    if 'width' in hint and hint['width'] is not None: w = int(hint['width'])
                    if 'height' in hint and hint['height'] is not None: h = int(hint['height'])

                # print "Scale", row, col, w, h
                img = img.scaled(w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

            p = QtGui.QPixmap()
            if img != None:
                p.convertFromImage(img)

            pixmaps.append(p)

        # print "Caching", row, col, path
        self._imageCache[path] = pixmaps
        self.dataChanged.emit(self.index(row, col), self.index(row, col))
        return val

    def headerData(self, col, orientation, role):
        if not QtCore: return
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col >= len(self._labels):
                return None

            return unicode(self._labels[col])

        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return unicode('%03d' % (col+1))

        return None

# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX
import wallaby.FXUI as FXUI

from wallaby.qt_combat import *

import sys, re, copy
from wallaby.frontends.qt.meta import *
from wallaby.pf.room import House
from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.editor import *

class BaseWidget(object):
    widgets = []

    def __init__(self, baseType, *params):
        self.__baseType = baseType

        self._config = {}
        self.resetWallabyTemplate()

        for key in self.wallabyProperties.keys():
            self.resetConfig(key)

        self._configDoc = None
        self.wallabyType = self.__class__.__name__

        self._registered    = False
        self._hasConflict   = False
        self._currentValue  = None
        self._conflictValues = None

        self._configViewerRegistered = False

        self._overlay = None
        self._lastConfig = None

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._showConflictContextMenu)

        self._template = None
        self._ignorePalette = False

    def registerPalette(self):
        palette = self.childPalette()
        self._origPalette = palette.resolve(palette)
        self._disabledSet = set()
  
        brush = QtGui.QBrush(QtGui.QColor(0, 34, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.setAllStateBrush(palette, QtGui.QPalette.ButtonText, brush)
        self.setAllStateBrush(palette, QtGui.QPalette.Text, brush)
        self._pendingPalette = palette.resolve(palette)
      
        brush.setColor(QtGui.QColor(255, 0, 0)) 
        self.setAllStateBrush(palette, QtGui.QPalette.ButtonText, brush)
        self.setAllStateBrush(palette, QtGui.QPalette.Text, brush)
        self.setAllStateBrush(palette, QtGui.QPalette.WindowText, brush)
        self._faultyPalette = palette.resolve(palette)

        self._noConflictPalette = self._origPalette

    def registerConfigViewer(self):
        if not self._ignorePalette:
            self.registerPalette()
        # if not FX.app: return

        self._template = self.getWallabyTemplate()
        if self._template is None:
            self._template = unicode(self.objectName())

        if not self._configViewerRegistered:
            self._configViewerRegistered = True
            House.get("__CONFIG__").catch(Viewer.In.Refresh, self._configChanged)
            House.get("__CONFIG__").catch(Viewer.In.Document, self._configDocChanged)

    def _configDocChanged(self, pillow, doc):
        self._configDoc = doc
   
        if doc != None and doc.get("widgets." + self._template) == None:
            doc.set("widgets." + self._template, self._config)
            House.get("__CONFIG__").throw(Editor.Out.FieldChanged, "widgets." + self._template)

        self._configChanged(None, "widgets." + self._template)

    def _configChanged(self, pillow, path):
        if not self._configDoc or not Viewer.matchPath("widgets." + self._template, path): return
        config = self._configDoc.get("widgets." + self._template)

        if config is not None:
            import json

            if self._lastConfig == None or json.dumps(self._lastConfig, sort_keys=True) != json.dumps(config, sort_keys=True):
                for k, v in config.items():
                    if k == "wallabyType" or (k in self.wallabyProperties and self.wallabyProperties[k].readOnly): 
                        continue
                    self._config[k] = v

                for k, v in self._config.items():
                    if k == "wallabyType" or (k in self.wallabyProperties and self.wallabyProperties[k].readOnly) or k not in config: 
                        config[k] = v

                self._lastConfig = copy.deepcopy(config)

                if self.room != None and len(self.room) > 0: House.get(self.room) # Implicit room creation...
                self.deregister()
                self.register()

    def createOverlay(self):
        if self._overlay == None: 
            from wallabyOverlay import WallabyOverlay
            self._overlay = WallabyOverlay(FXUI.mainWindow, self)

        self._overlay.hide()
        self.resizeOverlay()
        return self._overlay

    def overlayLabel(self):
        label = []
        try:
            room = self.room
            label.append(room)
        except:
            label.append(None)

        try:
            path = self.path
            if path != None: label.append(path)
        except:
            pass

        return label

    def overlayRect(self):
        r = self.visibleRegion().boundingRect()
        r.setX(0)
        r.setY(0)
        return r

    def resizeOverlay(self):
        if self._overlay != None:
            r = self.overlayRect()
            geo = self._overlay.geometry()

            geo.moveTo(self.mapTo(FXUI.mainWindow, QtCore.QPoint(r.x(), r.y())))
            geo.setWidth(r.width())
            geo.setHeight(r.height()) 

            self._overlay.setBaseGeometry(geo)

    def showOverlay(self):
        if QtGui.QWidget.isVisible(self):
            self.createOverlay().show()

    def hideOverlay(self):  
        if self._overlay:
            self._overlay.hide()

    def destroyOverlay(self):
        if self._overlay:
            self._overlay.hide()
            self._overlay.setParent(None)
            self._overlay.deleteLater()
            self._overlay = None

    def _setOrigPalette(self):
        self._noConflictPalette = self._origPalette
        if self._hasConflict == False:
            self.setPalette(self._noConflictPalette)

    def _setPendingPalette(self):
        self._noConflictPalette = self._pendingPalette
        if self._hasConflict == False:
            self.setPalette(self._noConflictPalette)

    def _setFaultyPalette(self):
        self._noConflictPalette = self._faultyPalette
        if self._hasConflict == False:
            self.setPalette(self._noConflictPalette)

    def getMenuEntries(self):
        return {}

    def _showConflictContextMenu(self, pos):
        globalPos = self.mapToGlobal(pos)

        if not self._hasConflict: 
            menuEntries = self.getMenuEntries()
            if menuEntries == None or len(menuEntries) == 0:
                return

            menu = QtGui.QMenu(self)
            for label, action in menuEntries.items():
                pillow = action
                feathers = None

                if isinstance(action, (list, tuple)): 
                    if len(action) == 2:
                        pillow, feathers = action
                    else:
                        pillow = action.pop(0)

                act = menu.addAction(label)
                act.pillow = pillow
                act.feathers = feathers

            action = menu.exec_(globalPos)
            if action != None:
                House.get(self.room).throw(action.pillow, act.feathers)

            return

        menu = QtGui.QMenu()
        if isinstance(self._currentValue, (list, dict)):
            mineAction = QtGui.QAction(FXUI.mineIcon, "use " + str(len(self._currentValue)) + " Item(s) (mine)", self)
        else:
            mineAction = QtGui.QAction(FXUI.mineIcon, "use >" + unicode(self._currentValue) + "< (mine)", self)

        menu.addAction(mineAction)

        mineAllAction = QtGui.QAction(FXUI.mineIcon, "use mine", self)
        menu.addAction(mineAllAction)

        theirsAction = []
        theirsAllAction = []
        
        for user, c in self._conflictValues:
            if user == None: user = "unknown"

            if isinstance(c, (list, dict)):
                act = QtGui.QAction(FXUI.theirsIcon, "use " + str(len(c)) + " Item(s) ("+user+")", self)
            else:
                act = QtGui.QAction(FXUI.theirsIcon, "use >" + unicode(c) + "< ("+user+")", self)
            theirsAction.append(act)
            menu.addAction(act)

            act = QtGui.QAction(FXUI.theirsIcon, "use theirs ("+user+")", self)
            theirsAllAction.append(act)
            menu.addAction(act)

        act = menu.exec_(globalPos)

        if act != None:
            if act == mineAllAction:
                self._resolve(self._currentValue, mine=True)
            elif act == mineAction:
                self._resolve(self._currentValue)
            else:
                if act in theirsAction:
                    idx = theirsAction.index(act)
                    self._resolve(self._conflictValues[idx][1])
                else:
                    idx = theirsAllAction.index(act)
                    self._resolve(self._conflictValues[idx][1], theirs=idx)

            self._conflict(False, self._currentValue, self._conflictValues)

    def _resolve(self, value):
        pass

    def _conflict(self, hasConflict, currentValue, conflictValues):
        if hasConflict:
            self._hasConflict   = True
            self.setPalette(self._faultyPalette)
        else:
            self._hasConflict = False
            self.setPalette(self._noConflictPalette)

        self._currentValue  = currentValue
        self._conflictValues = conflictValues

    def setAllStateBrush(self, palette, t, brush):
        palette.setBrush(QtGui.QPalette.Active  , t, brush)
        palette.setBrush(QtGui.QPalette.Inactive, t, brush)
        palette.setBrush(QtGui.QPalette.Disabled, t, brush)

    def childPalette(self):
        return self.palette()

    def setChildPalette(self, p):
        FX.trace("DEFAULT SET CHILD PALETTE")
        self.setPalette(p)

    def register(self):
        self._registered = True

    def deregister(self, remove=False):
        pass

    def getConfig(self, key=None, type=None, raw=False):
        key = unicode(key)

        if type == None: 
            if key not in self.wallabyProperties: return None
            type = self.wallabyProperties[key].type

        if self.wallabyProperties[key].readOnly:
            return self.wallabyProperties[key].default

        if type == "string":
            if key not in self._config: 
                return self.wallabyProperties[key].default

            val = self._config[key]

            if val == None:
                pass
            else:
                if val == 'None': val = None

            if not raw and val != None and key in ('room', 'path') and len(val) > 0 and val[0] in ('|', '.'):
                p = self.parentWidget()
                while p != None:
                    if isinstance(p, BaseWidget):
                        prefix = p.getConfig(key, type)
                        if prefix != None:
                            return prefix + val
                        else:
                            return val
                    else:
                        p = p.parentWidget()
                
            return val

        elif type in ("float", "double", "int", "bool"):
            if key not in self._config:
                return self.wallabyProperties[key].default

            if type in ("float", "double"):
                try:
                    return float(self._config[key])
                except:
                    return 0.0
            elif type in ("int"):
                try:
                    return int(float(self._config[key]))
                except:
                    return 0
            elif type in ("bool"):
                try:
                    return bool(int(float(self._config[key])))
                except:
                    return False

        elif type == "dict":
            if key not in self._config: 
                return {}

            val = self._config[key]

            if val == None:
                return {}
            else:
                return copy.deepcopy(val)

        elif type == "list":
            if key not in self._config: 
                return []

            val = self._config[key]

            if val == None:
                return []
            else:
                return copy.deepcopy(val)

    def setConfig(self, val, key=None, type=None):
        key = unicode(key)

        if type == None: 
            if key not in self.wallabyProperties: return
            type = self.wallabyProperties[key].type

        if self.wallabyProperties[key].readOnly: return

        if type == "string":
            if val != None:
                val = str(val)

        elif type == "dict":
            if val != None and not isinstance(val, dict):
                dct = {}
                for e in val:
                    if ':' in e:
                        k, v = unicode(e).split(':')
                        try:
                            jsonString = u'{"value":' + v + u'}' 
                            import json
                            obj = json.loads(jsonString)
                            dct[k] = obj['value']
                        except Exception as ex:
                            print "ERROR - Json parse error (", ex, ")", jsonString

                val = dct

        elif type == "list":
            if val != None and not isinstance(val, list):
                lst = []
                for i in val:
                    lst.append(unicode(i))

                val = lst

        elif type in ("bool", "int", "float", "double"):
            pass

        self._config[key] = val
        if self._configDoc != None:
            config = self._configDoc.get("widgets." + self._template)
            config[key] = val
        
    def resetConfig(self, key=None, type=None):
        key = unicode(key)

        if type == None: type = self.wallabyProperties[key].type
        default = self.wallabyProperties[key].default

        if default is not None:
            self._config[key] = default
        else:
            if type == "string":
                self._config[key] = None
            elif type == "bool":
                self._config[key] = False
            elif type == "int":
                self._config[key] = 0
            elif type in ("float", "double"):
                self._config[key] = 0.0
            elif type == "list":
                self._config[key] = []
            elif type == "dict":
                self._config[key] = {}

    def getWallabyTemplate(self):
        if self._wallabyTemplate == "None" or len(self._wallabyTemplate) == 0: return None
        return unicode(self._wallabyTemplate)

    def setWallabyTemplate(self, d):
        if d == None or len(d) == 0: self._wallabyTemplate = "None"
        else: 
            self._wallabyTemplate = unicode(d)
            self.registerConfigViewer()

    def resetWallabyTemplate(self):
        self._wallabyTemplate = "None"


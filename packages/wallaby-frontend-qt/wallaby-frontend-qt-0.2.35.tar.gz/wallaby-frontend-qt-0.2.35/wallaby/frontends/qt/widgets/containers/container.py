# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.frontends.qt.meta import *
import os, string

from wallaby.qt_combat import *
from ..baseWidget import *
from ..logics import *

class Container(BaseWidget, EnableLogic):
    __metaclass__ = QWallabyMeta

    room = Meta.property("string")
    sheets = Meta.property("string")

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)
        EnableLogic.__init__(self)

        self._sheetPrototypes = {}
        self._lastSheets = None
        self.sheetCache = {}
        self._sheet = None

    def activate(self):
        if self._sheet is not None:
            self.addChildWidget(self._sheet)

            # also activate nested containers
            containers = self._sheet.findChildren(Container)
            for c in containers: c.activate()

    def isMultiPage(self):
        return False

    def getChildWidget(self, pos):
        return None

    def childCount(self):
        return 0

    def addChildWidget(self, w):
        pass

    def removeChildWidget(self, w):
        w.hide()
        w.setParent(None)
        w.deleteLater()

    def clear(self):
        while self.childCount() > 0:
            widget = self.getChildWidget(0)
            if widget is None: next

            widgets = widget.findChildren(BaseWidget)
            for w in widgets:
                w.deregister(remove=True)
                w.destroyOverlay()
                # BaseWidget.widgets.remove(w)

            if isinstance (widget, BaseWidget):
                widget.deregister(remove=True)
                widget.destroyOverlay()
                # BaseWidget.widgets.remove(w)
                # BaseWidget.widgets.remove(widget)

            self.removeChildWidget(widget)

    def loadUIFiles(self):
        # Do not reload widgets if not changed
        if self.sheets is None or self.sheets == self._lastSheets: return
        self._lastSheets = self.sheets

        self.clear()

        isheets = []

        self._sheetPrototypes = {}

        import wallaby.frontends as frontends
        from twisted.plugin import getCache

        for p in FX.packagePath(FX.appModule + ".isheet"): isheets.append(p)
        for frontend in getCache(frontends):
            for p in FX.packagePath("wallaby.frontends." + frontend + ".isheet"): isheets.append(p)

        import os
        for path in isheets:
            root = re.sub(r'[/\\]','.', path).replace('..', '')
            root = re.sub(r'^.*wallaby\.', 'wallaby.', root)
            files = os.listdir(path)
            for file in files:
                if '.py' in file and '.pyc' not in file and 'UI_' in file:
                    basename, ext = os.path.splitext(file)

                    if ext != '.py': continue

                    mod = FX.imp(root + '.' + basename)
                    if mod == None: continue

                    cls = basename[0] + string.lower(basename[1]) + basename[2] + string.upper(basename[3]) + basename[4:]
    
                    sheetName = unicode(basename.replace('UI_', ''))

                    sheetCache = None

                    if sheetName in self._sheetPrototypes: 
                        continue

                    if re.match(self.sheets, sheetName) is None: 
                        continue

                    if not self.isMultiPage():
                        p = self.parent()
                        while p != None and (not isinstance(p, Container) or not p.isMultiPage()):
                            p = p.parent()

                        if p is not None:
                            sheetCache = p.sheetCache

                            if sheetName in sheetCache:
                                self._sheet = sheetCache[sheetName]
                                return

                    if not cls in mod.__dict__:
                        for key, val in mod.__dict__.items():
                            if key.startswith("Ui_"):
                                cls = key
                                break

                    if not cls in mod.__dict__: continue

                    self._sheetPrototypes[sheetName] = mod.__dict__[cls]

                    sheet = QtGui.QWidget(self)
                    sheet.ui = self._sheetPrototypes[sheetName]()
                    sheet.ui.setupUi(sheet)
                    sheet.setObjectName(sheetName + "Sheet") 

                    if sheetCache is not None:
                        self._sheet = sheet
                        sheetCache[sheetName] = sheet
                        # also add the cached sheet to the current widget
                        # to allow nested widgets to also be loaded

                    self.addChildWidget(sheet)

    def deregister(self, remove):
        EnableLogic.register(self, remove)

    def register(self):
        EnableLogic.register(self)

        if self.sheets != None:
            self.loadUIFiles()

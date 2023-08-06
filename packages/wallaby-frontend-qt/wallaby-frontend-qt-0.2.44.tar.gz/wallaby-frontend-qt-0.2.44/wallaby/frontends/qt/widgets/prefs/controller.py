# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..baseWidget import *
from wallaby.pf.peer.pref import *
from twisted.internet import defer
from UI_prefController import *
from sheet import *
from ..logics import *

class PrefController(QtGui.QWidget, Ui_PrefController, BaseWidget, EnableLogic):
    __metaclass__ = QWallabyMeta

    room = Meta.property("string")
    path = Meta.property("string")

    configDocId = Meta.property("string")

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QWidget, *args)
        EnableLogic.__init__(self)
        self._pref = None
        self._viewer = None
        self._idx = 0
        self._sheetPrototypes = {}
        self._idxToPreference = []

        self.setupUi(self)

        self.scrollArea.setWidgetResizable(True)
        self._layout = QtGui.QVBoxLayout(self.content)

        self.prefAdd.clicked.connect(self.addPrefWidget)

        self._loading = False
        self._reload = False

        # self.setEnabled(False)

    def checkEnableUpDowns(self):
        for i in range(self._layout.count()):
            item = self._layout.itemAt(i)
            item.widget().moveUp.setEnabled(True)
            item.widget().moveDown.setEnabled(True)

        if self._layout.count() < 1: return
        self._layout.itemAt(0).widget().moveUp.setEnabled(False)
        self._layout.itemAt(self._layout.count()-1).widget().moveDown.setEnabled(False)

    def overlayRect(self):
        r = BaseWidget.overlayRect(self)
        r.moveTo(r.x(), r.height()-60)
        r.setHeight(min(20, r.height()))
        return r

    def movePrefSheet(self, pos, direction):
        doc = self._pref.document()
        if doc == None: return

        list = doc.get(self.path)
        if pos > len(list): return

        if direction and pos == 0: return
        if not direction and pos == len(list)-1: return

        if direction:
            list[pos-1], list[pos] = list[pos], list[pos-1]

            item = self._layout.takeAt(pos)
            self._layout.insertWidget(pos-1, item.widget())

            item.widget().decrementIndex()
            self._layout.itemAt(pos).widget().incrementIndex()
        else:
            list[pos+1], list[pos] = list[pos], list[pos+1]

            item = self._layout.takeAt(pos)
            self._layout.insertWidget(pos+1, item.widget())

            item.widget().incrementIndex()
            self._layout.itemAt(pos).widget().decrementIndex()

        self.checkEnableUpDowns()

    def move(self, f, t):
        if f < t: t-=1
        if f==t: return

        doc = self._pref.document()
        if doc == None: return

        list = doc.get(self.path)
        if t > len(list): return

        data = list[f]
        del list[f]
        list.insert(t, data)

        item = self._layout.takeAt(f)

        self._layout.insertWidget(t, item.widget())

        for i in range(self._layout.count()):
            item = self._layout.itemAt(i)
            item.widget().setIndex(i)

        self.checkEnableUpDowns()

        self._pref._throw(Editor.Out.FieldChanged, self.path + ".")

    def addPrefWidget(self):
        if len(self._idxToPreference) == 0 or self.prefSelect.count() == 0: return

        sheet = self._idxToPreference[self.prefSelect.currentIndex()]
        from twisted.internet import reactor
        if sheet is not None:
            print "Create sheet manual"
            self.createSheet(unicode(sheet), locked=False, scrollTo=True)

    def register(self):
        EnableLogic.register(self)
        self._pref = Pref(self.room, self, self.configDocId, self.path)
        self._viewer = Viewer(self.room, self._listChanged, self.path)

        self.clear()
        self.loadUIFiles()

    def clear(self):
        item = self._layout.takeAt(0)
        while item is not None:
            widget = item.widget()

            widgets = widget.findChildren(BaseWidget)
            for w in widgets:
                w.deregister(remove=True)
                # BaseWidget.widgets.remove(w)

            if isinstance (widget, BaseWidget):
                widget.deregister(remove=True)
                # BaseWidget.widgets.remove(widget)

            widget.hide()
            widget.setParent(None)
            widget.deleteLater()
            item = self._layout.takeAt(0)

        self.update()
        self._idx = 0

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        if self._pref != None: self._pref.destroy(remove)
        if self._viewer != None: self._viewer.destroy(remove)
        self._viewer = None
        self._pref = None

    def _listChanged(self, list):
        self._pref.isReady(ignoreVersion=True)

    def load(self):
        if self._loading:
            self._reload = True
            return 

        self._loading = True

        doc = self._pref.document()
        config = self._pref.configDoc()

        if doc is None: 
            self.clear()
            self._checkReload()
            return

        self.prefSelect.clear()
        self._idxToPreference = []
        titles = {}

        for preference in self._sheetPrototypes:
            title = config.get("sheets." + preference + ".title")
            if title is not None:
                titles[title] = preference
            else:
                titles[preference] = preference

        for k, v in sorted(titles.items()):
            self._idxToPreference.append(v)
            self.prefSelect.addItem(k)

        list = doc.get(self.path)
        if list is None: 
            self.clear()
            self._checkReload()
            return

        # Delete all widgets that do not match the doc type
        items = []
        for i in range(self._layout.count()):
            items.append(self._layout.itemAt(i).widget())
            
        n = len(items)

        if abs(n-len(list)) > 4:
            self.clear()
            items = []
            n = 0
        else:
            i = w = 0
            while i < len(list):
                sheet = list[i]
                if '_sheet' not in sheet: 
                    continue

                if w < len(items):
                    item = items[w]
                    if item.type() != sheet['_sheet']:
                        # print "Delete", item.type(), w
                        del items[w]
                        self.remove(w, changeDoc=False)
                        n-=1
                        i-=1
                    else:
                        w+=1
                i+=1

            cnt = len(list)

            while len(items) > cnt:
                del items[cnt]
                n-=1
                self.remove(cnt, changeDoc=False)

        from twisted.internet import reactor

        # Lock all existing sheets
        for i in range(0, n):
            items[i].setIndex(i)
            items[i].lock()

        # print "creating", (len(list)-n), "sheets"

        # Create all new sheets
        for i in range(n,len(list)):
            sheet = list[i]
            if "_sheet" not in sheet: continue
            # print "CreateSheet", i
            self.createSheet(sheet["_sheet"])

        # Only configure if new sheets available
        if len(list) > n:
            self._configured(None)
        else:
            self._loading = False

    def _configured(self, ignoredparam):
        self._pref.updateAll()
        self._checkReload()

    def _checkReload(self):
        self._loading = False

        if self._reload:
            self._reload = False
            self.load()
    
    def loadUIFiles(self):
        self._sheetPrototypes = {}

        prefs = []

        import wallaby.frontends as frontends
        from twisted.plugin import getCache

        for p in FX.packagePath(FX.appModule + ".prefs"): prefs.append(p)
        for frontend in getCache(frontends):
            for p in FX.packagePath("wallaby.frontends." + frontend + ".prefs"): prefs.append(p)

        import os
        for path in prefs:
            root = re.sub(r'[/\\]','.', path).replace('..', '')
            root = re.sub(r'^.*wallaby\.', 'wallaby.', root)
            files = os.listdir(path)
 
            for file in files:
                if '.py' in file and '.pyc' not in file and 'UI_' in file:
                    basename, ext = os.path.splitext(file)
                    if ext == '.py':
                        mod = FX.imp(root + '.' + basename)
                        print "Loading prefs sheet", root + '.' + basename, mod
                        if mod == None: continue
   
                        import string 
                        cls = basename[0] + string.lower(basename[1]) + basename[2] + string.upper(basename[3]) + basename[4:]
    
                        sheetName = unicode(basename.replace('UI_', ''))
    
                        if not cls in mod.__dict__: continue
                        self._sheetPrototypes[sheetName] = mod.__dict__[cls]
    
    def remove(self, idx, changeDoc=True):
        item = self._layout.takeAt(idx)
        if item is not None:
            for i in range(idx, self._layout.count()):
                self._layout.itemAt(i).widget().decrementIndex()
    
            widget = item.widget()
            widgets = widget.findChildren(BaseWidget)
            for w in widgets:
                w.deregister(remove=True)
                # BaseWidget.widgets.remove(w)
    
            if isinstance (widget, BaseWidget):
                widget.deregister(remove=True)
                # BaseWidget.widgets.remove(widget)

            widget.hide()
            widget.setParent(None)
            widget.deleteLater()
    
            if changeDoc:
                doc = self._pref.document()
                if doc != None: 
                    list = doc.get(self.path) 
                    if list is not None and len(list) > idx:
                        del list[idx]

                    self._pref._throw(Editor.Out.FieldChanged, self.path + ".")
    
            self._idx -= 1
 
        from twisted.internet import reactor
        reactor.callLater(0, self.checkEnableUpDowns)
    
    def createSheet(self, name, locked=True, scrollTo=False):
        if not self._pref: return
    
        if self._pref.document() == None or self._pref.configDoc() == None: 
            self._pref.noDocument()
            return
    
        if name not in self._sheetPrototypes:
            self._pref.notFound(name)
            return
    
        doc = self._pref.document()
        configDoc = self._pref.configDoc()
    
        proto = configDoc.get("sheets."+name+".proto")
        if proto is None:
            proto = {}  
    
        title = configDoc.get("sheets."+name+".title")
        if title is None:
            title = name  
    
        prefix = self.path
    
        path = prefix + "." + unicode(self._idx)
        if doc.get(prefix) == None:
            doc.set(prefix, [])
    
        # PRINT DATA
        #print "DATA ", doc._data, prefix
    
        list = doc.get(prefix)
        if self._idx > len(list)-1:
            list.append(copy.deepcopy(proto))
        else:
            doc.merge(path, proto)
    
        #print " ARUMENTS ", path, name, doc._data
        doc.set(path + "._sheet", name) 

        # print "Creating sheet", path
    
        sheet = PrefSheet(name, self.room, prefix, self, self._idx, title, locked=locked)
        self._idx += 1
        
        sheet.ui = self._sheetPrototypes[name]()
        sheet.ui.setupUi(sheet.content)
    
        self._layout.addWidget(sheet)

        self.checkEnableUpDowns()
    
        self._pref._throw(Editor.Out.FieldChanged, path + ".")
    
        if scrollTo:
            self.scrollArea.ensureWidgetVisible(sheet, 50, 100)
    
        self.update()

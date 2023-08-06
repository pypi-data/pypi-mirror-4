# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from wallaby.pf.peer.enabler import *
from wallaby.pf.peer.documentPathEnabler import *
from wallaby.pf.peer.actionButtonPeer import *
from wallaby.pf.peer.triggeredPillows import *
from wallaby.frontends.qt.meta import *

class WidgetNotSubclassingEnableLogicError(Exception):
    pass

class ContextMenuLogic(object):
    __metaclass__ = QWallabyMeta

    contextMenuEntries  = Meta.property("dict")

    def getMenuEntries(self):
        return self.contextMenuEntries

class TriggeredPillowsLogic(object):
    __metaclass__ = QWallabyMeta

    triggeredPillows = Meta.property("dict")

    def __init__(self):
        self._triggeredPillowsPeer = None
        self._triggeredViewer = None
        self._triggeredValue = None
        self._triggeredPath = None
        self._triggeredDoc = None

    def trigger(self, trigger, arg=None):
        if self._triggeredPillowsPeer != None: return self._triggeredPillowsPeer.trigger(trigger, arg, doc=self._triggeredDoc, path=self._triggeredPath, value=self._triggeredValue)
        return False

    def _newTriggeredValue(self, value):
        self._triggeredDoc = self._triggeredViewer.document()
        self._triggeredValue = value

    def register(self):
        try:
            if self.path != None and len(self.path) > 0:
                self._triggeredPath = self.path
        except: pass 

        if len(self.triggeredPillows) > 0:
            self._triggeredPillowsPeer = TriggeredPillows(self.room, self.triggeredPillows)

            if self._triggeredPath is not None: 
                self._triggeredViewer = Viewer(self.room, self._newTriggeredValue, self.path, raw=True)

    def deregister(self, remove=False):
        if self._triggeredViewer: self._triggeredViewer.destroy(remove)
        if self._triggeredPillowsPeer: self._triggeredPillowsPeer.destroy(remove)       
        self._triggeredViewer = None
        self._triggeredPillowsPeer = None

class EnableLogic(object):
    __metaclass__ = QWallabyMeta

    room            = Meta.property("string")
    enableFeathers  = Meta.property("list")
    enablePath      = Meta.property("string")
    enablePathValue = Meta.property("string")
    hideIfDisabled  = Meta.property("bool")

    def __init__(self):
        self._enabler = None
        self._documentPathEnabler = None

        self._enabledByEnabler = True
        self._enabledByEditor = True
        self._enabledByRealtime = True

    def deregister(self, remove=False):
        if self._enabler: self._enabler.destroy(remove)
        if self._documentPathEnabler: self._documentPathEnabler.destroy(remove)

        self._enabler = None
        self._documentPathEnabler = None

    def register(self):
        if len(self.enableFeathers) > 0:
            self._enabler = Enabler(self.room, self._enablerSetEnabled, self.enableFeathers)

        if self.enablePath != None and self.enablePathValue != None and self.enablePath != "":
            self._documentPathEnabler = DocumentPathEnabler(self.room, self._enablerSetEnabled, self.enablePath, self.enablePathValue)

    def _editorSetDisabled(self, disabled):
        self._enabledByEditor = not disabled
        self._callSetEnabled()

    def _enablerSetEnabled(self, enabled):
        self._enabledByEnabler = enabled
        self._callSetEnabled()

    def _realtimeSetEnabled(self, enabled):
        self._enabledByRealtime = enabled
        self._callSetEnabled()

    def _callSetEnabled(self):
        enabled = self._enabledByEnabler and self._enabledByEditor and self._enabledByRealtime
        self._setEnabled(enabled)

    def _setEnabled(self, enabled):
        if self.hideIfDisabled:
            self.setVisible(enabled)
        else:
            self.setEnabled(enabled)

class QueryLogic(object):
    __metaclass__ = QWallabyMeta

    view = Meta.property("string")
    viewArguments = Meta.property("string")
    viewIdentifier = Meta.property("string")
    dataView = Meta.property("string")

    def __init__(self):
        self._queryPeer = None

    def register(self, **viewerArgs):
        from wallaby.pf.peer.multiViewer import MultiViewer
        self._queryPeer = MultiViewer(self.room, self.view, self.viewIdentifier, self.viewArguments, self.dataView, self, autoUpdate=True)

    def initialData(self): 
        pass

    def deregister(self, remove=False):
        if self._queryPeer: self._queryPeer.destroy(remove)
        self._queryPeer = None

class ViewLogic(object):
    __metaclass__ = QWallabyMeta

    room = Meta.property("string")
    path = Meta.property("string")

    def __init__(self, viewerClass, setContentCB):
        self._viewerClass = viewerClass
        self._setContentCB = setContentCB
        self._viewer = None

    def register(self, **viewerArgs):
        if self.path and self._setContentCB: self._viewer = self._viewerClass(self.room, self._setContentCB, self.path, **viewerArgs)

    def deregister(self, remove=False):
        if self._viewer: self._viewer.destroy(remove)
        self._viewer = None

class EditLogic(object):
    __metaclass__ = QWallabyMeta

    room         = Meta.property("string")
    path         = Meta.property("string")
    selectOnEdit = Meta.property("bool")

    def __init__(self, editorClass, getContentCB):
        self._editorClass = editorClass
        self._getContentCB = getContentCB
        self._editor = None

    def register(self, **editorArgs):
        if not isinstance(self, EnableLogic): raise WidgetNotSubclassingEnableLogicError()

        if self.path and self._getContentCB: self._editor = self._editorClass(self.room, None, self._getContentCB, self._editorSetDisabled, self._conflict, self.path, selectOnEdit=self.selectOnEdit, **editorArgs)

    def deregister(self, remove=False):
        if self._editor: self._editor.destroy(remove)
        self._editor = None

class EnterPillowLogic(object):
    __metaclass__ = QWallabyMeta

    enterPillow   = Meta.property("string")
    enterFeathers = Meta.property("string")
    enterTab      = Meta.property("string")

    def __init__(self, signal):
        self._enterPeer = None
        signal.connect(self._returnPressed)

    def register(self):
        if self.enterPillow != None:
            self._enterPeer = ActionButtonPeer(self.room, self.enterPillow, self.enterFeathers, tab=self.enterTab)

    def deregister(self, remove=False):
        if self._enterPeer: self._enterPeer.destroy(remove)
        self._enterPeer = None

    def _returnPressed(self):
        if self._enterPeer:
            self._enterPeer.buttonClicked()

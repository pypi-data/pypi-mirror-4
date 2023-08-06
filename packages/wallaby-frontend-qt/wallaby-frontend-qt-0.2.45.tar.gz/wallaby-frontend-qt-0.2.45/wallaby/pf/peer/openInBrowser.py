# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *
from viewer import *
from wallaby.backends.couchdb import *
from wallaby.qt_combat import *

class OpenInBrowser(Peer):
    Open = Pillow.In

    Receiving = [
        Viewer.In.Document
    ]

    def __init__(self, room, databaseName=None):
        Peer.__init__(self, room)

        self._id     = None
        self._dbName = databaseName

        self._catch(OpenInBrowser.In.Open, self._open)
        self._catch(Viewer.In.Document, self._docArrived)

        self._doc = None

    def _open(self, pillow, feathers):
        if feathers != None and len(feathers) > 0:
            if feathers.startswith("/"):
                url = QtCore.QUrl(dbURL+feathers)
                QtGui.QDesktopServices.openUrl(url)
                return

            if '/' not in feathers and '.' in feathers and self._doc != None:
                url = self._doc.get(feathers) 
                if url != None:
                    self._open(None, url)
                return

            url = QtCore.QUrl(feathers)
            QtGui.QDesktopServices.openUrl(url)
            return

        if self._id != None:
            dbURL = Database.getURLForDatabase(self._dbName)
            if dbURL == None: return

            if self._dbName == None:
                self._dbName = Database.getDefaultDatabaseName()

            url = QtCore.QUrl(dbURL+'/_utils/document.html?'+self._dbName+'/'+self._id)
            QtGui.QDesktopServices.openUrl(url)

    def _docArrived(self, pillow, doc):
        self._doc = doc
        if doc != None:
            self._id = doc.documentID

    def initialize(self):
        pass

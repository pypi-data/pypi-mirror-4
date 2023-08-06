# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from wallaby.qt_combat import *
from viewer import Viewer
from wallaby.backends.couchdb import *

class AttachmentOpener(Peer):
    Open = Pillow.In

    def __init__(self, room, databaseName=None):
        Peer.__init__(self, room)
        self._viewer = Viewer(room, self._setID, '_id')

        self._databaseName = databaseName
        self._id = None
        self._catch(AttachmentOpener.In.Open, self._open)

    def _setID(self, value):
        self._id = value

    def _open(self, pillow, feather):
        if self._id != None:
            dbURL = Database.getURLForDatabase(self._databaseName)
            if dbURL == None: return

            if self._databaseName == None:
                self._databaseName = Database.getDefaultDatabaseName()

            print dbURL, self._databaseName, self._id, feather

            url = QtCore.QUrl(dbURL+'/'+self._databaseName+'/'+self._id+'/'+feather)
            QtGui.QDesktopServices.openUrl(url)

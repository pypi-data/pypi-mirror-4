# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from wallaby.qt_combat import *

from UI_mainWindow import Ui_MainWindow

from wallaby.pf.room import *
from wallaby.frontends.qt.baseWindow import *

import wallaby.backends.couchdb as couchdb
import wallaby.backends.elasticsearch as es

import app_rc

class MainWindow(BaseWindow, Ui_MainWindow):
    def __init__(self, quitCB, options):
        db = options.app
        if options.db is not None:
            db = options.db

        BaseWindow.__init__(self, "wallaby", options.app, options, quitCB, dbName=db)

        # set up User Interface (widgets, layout...)
        self.setupUi(self)

    def setConnectionSettings(self, options):
        if options and options.fx:
            options.server = "https://relax.freshx.de"
            options.couchPort = "443"
            options.esPort = "443/es"

        couch.Database.setURLForDatabase(self.dbName(), options.server + ":" + options.couchPort)
        es.Connection.setURLForIndex(None, options.server + ':' + options.esPort)

        if options and options.username != None and options.password != None:
            es.Connection.setLoginForIndex(None, options.username, options.password)

    def _credentialsArrived(self, pillow, feathers):
        pass

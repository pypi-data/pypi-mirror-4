#!/usr/bin/env python
# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.


import wallaby.FX as FX
import wallaby.FXUI as FXUI

from wallaby.qt_combat import *

import wallaby.frontends.qt.resource_rc as resource_rc
from wallaby.frontends.qt.loginDialog import *
import twisted.application.service
import sys, time

from twisted.internet import defer

import wallaby.frontends.qt.reactor.threadedselect as threadedselect

from wallaby.frontends.qt.baseqobject import *
from wallaby.common.fxLogger import *

from wallaby.pf.peer import *
from wallaby.pf.peer.debugger import *
from wallaby.pf.room import *

import signal
import wallaby.frontends.qt.resource_rc

import shutil

class WallabyApp(object):
    def __init__(self, appName = 'example', checkRoom = None, suggest = False, options=None):
        splash = None

        FXUI.app = QtGui.QApplication(sys.argv)
        FXUI.app.setApplicationName("wallaby - " + appName)

        for s in ['16', '32', '64', '128', '256']:
            FXUI.app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(':/icons/images/wallaby_logo_' + s + '.png')))

        pixmap = QtGui.QPixmap(":/images/images/wallaby_splash.png")
        splash = QtGui.QSplashScreen(pixmap)
        splash.show()
        splash.raise_()
        FXUI.app.processEvents()

        if USES_PYSIDE:
            import wallaby.frontends.qt.reactor.qtreactor as qtreactor
            qtreactor.install()
        else:
            threadedselect.install()
             
            from twisted.internet import reactor
            ii = Interleaver()
            reactor.interleave(ii.toInterleave)
            reactor.suggestThreadPoolSize(50)

        FXUI.mineIcon = QtGui.QIcon(':/icons/images/mine.png')
        FXUI.theirsIcon = QtGui.QIcon(':/icons/images/theirs.png')

        tapp = twisted.application.service.Application("gui")
        service  = FXLogger('wallaby.log')
        service.setServiceParent(tapp)
        service.startService()

        FX.appModule = 'wallaby.apps.' + appName

        try:
            from twisted.plugin import getCache
            pkg = __import__(FX.appModule, globals(), locals(), ["*"], 0)
            if pkg is not None and len(pkg.__path__) > 0 and os.path.exists(pkg.__path__[0]):
                FX.appPath = pkg.__path__[0]
            else:
                FX.appPath = os.path.join(".", "wallaby", "apps", appName)
        except:
            FX.appPath = os.path.join(".", "wallaby", "apps", appName)

        try:
            print "importing", FX.appModule
            mod = FX.imp(FX.appModule + '.mainWindow', False)
        except:
            mod = None

        if mod == None:
            FX.crit('Module', FX.appModule, 'not found')
            reactor.callWhenRunning(self.myQuit)
            if USES_PYSIDE: reactor.runReturn()
            FXUI.app.exec_()
            return

        try:
            FXUI.mainWindow = mod.MainWindow(self.myQuit, options)
        except Exception as e:
            import traceback
            traceback.print_exc(file=sys.stdout)

            from twisted.internet import reactor
            reactor.callWhenRunning(self.myQuit)
            if USES_PYSIDE: reactor.runReturn()
            FXUI.app.exec_()
            return

        FXUI.mainWindow.setSplash(splash)

        from twisted.internet import reactor
        reactor.callWhenRunning(self.run, mod, options, checkRoom)

        FXUI.mainWindow.enabled = False
        FXUI.mainWindow.configure()
        FXUI.mainWindow.show()
        FXUI.mainWindow.raise_()

        signal.signal(signal.SIGINT, self.sigint_handler)
        signal.signal(signal.SIGTERM, self.sigint_handler)

        # self.gc = GarbageCollector(FXUI.mainWindow, True)

        if USES_PYSIDE: reactor.runReturn()
        FXUI.app.exec_()

    @defer.inlineCallbacks
    def run(self, mod, options, checkRoom): 
        if options is not None:
            authenticated = yield FXUI.mainWindow.authenticated(options.username, options.password, options)
        else:
            authenticated = yield FXUI.mainWindow.authenticated()

        count = 0
        while not authenticated:
            if count == 3: self.realQuit(0)

            dlg = LoginDialog()
            code = dlg.exec_()

            if code == 0: self.realQuit(0)

            try:
                authenticated = yield FXUI.mainWindow.authenticated(unicode(dlg.userEdit.text()), unicode(dlg.pwdEdit.text()), options)
            except:
                return

            count += 1

        from twisted.internet import reactor

        if options is not None: FXUI.mainWindow.setDebuggedRooms(options.debug)
        FXUI.mainWindow.run(checkRoom)
        FXUI.mainWindow.enabled = True

    def realQuit(self, shuttime):
        if FXUI.app != None:
            if shuttime > 0:
                print "Shutdown in ", (shuttime-1), "seconds"
                from twisted.internet import reactor
                reactor.callLater(1, self.realQuit, shuttime-1)
                return

            from wallaby.frontends.qt.widgets.baseWidget import BaseWidget
            if FXUI.mainWindow is not None:
                for w in FXUI.mainWindow.findChildren(BaseWidget):
                    w.deregister(True)

            app = FXUI.app
            del FXUI.app
            del FXUI.mainWindow

            print "Stopping Reactor"
            from twisted.internet import reactor
            reactor.stop()

            FX.info("Stopping app")
            print "Stopping App"

            app.exit()
            # FXUI.app.quit()
            FX.info("Stopping reactor")
            FX.info("Bye")

            app = None

    def myQuit(self):
        print "Set shutdown flag"
        FX.shutdown = True
        FX.callShutdownCBs()
        shuttime = 0
        from twisted.internet import reactor
        print "Shutdown in ", shuttime, "seconds"
        reactor.callLater(1, self.realQuit, shuttime)

    def sigint_handler(self, *args):
        """Handler for the SIGINT signal."""
        self.myQuit()

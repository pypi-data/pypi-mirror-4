# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import sys
from thread import get_ident
import wallaby.FXUI as FXUI

from wallaby.qt_combat import *

class BaseQObject(QtCore.QObject):
    MAIN_THREAD_ID = 0
    
    def __init__(self):
        QtCore.QObject.__init__(self)
    #    self.installEventFilter(self)
        self.event = None

    # def eventFilter(self,obj,event):
    #   # FIXME:  This is a workaround for an unexplained bug
    #   # The events were getting posted through postEVentWithCallback()
    #   # But the event() method wasn't getting called.  But the eventFilter()
    #   # method is getting called.  
    #   if event.type()==QEvent.User:
    #       cb = event.__dict__.get('callback')
    #       if cb: 
    #           self._doEvent(event)
    #       return True
    #   return QObject.eventFilter(self,obj,event)

    # def _doEvent(self,event):
    #    cb = event.__dict__.get('callback')
    #    if not cb: return
    #    data = event.__dict__.get('data')
    #    if data or type(data)==type(False): cb(data)
    #    else: cb()
    #    del event

    def event(self, event):
        if event.type()==QtCore.QEvent.User:
            # self._doEvent(event)

            cb = event.__dict__.get('callback')
            if not cb: return
            data = event.__dict__.get('data')
            if data or type(data)==type(False): cb(data)
            else: cb()
            del event

            return True
        return QtCore.QObject.event(self, event)

    def postEventWithCallback(self, callback, data=None):
        # if we're in main thread, just fire off callback
        if get_ident()==BaseQObject.MAIN_THREAD_ID:
            if data or type(data)==type(False): callback(data)
            else: callback()
        # send callback to main thread 
        else:
            event = QtCore.QEvent(QtCore.QEvent.User)
            event.callback = callback
            if data or type(data)==type(False): event.data = data
            # FXUI.app.postEvent(self, event, -1000)
            FXUI.app.postEvent(self, event)
            
class Interleaver(BaseQObject):
    def quit(self):
        from twisted.internet import reactor
        reactor.stop()
        
    def __init__(self):
        BaseQObject.__init__(self)

    def toInterleave(self, func, *args, **kwargs):
        # FX.debug('toInterleave(): %s'%(str(func)))
        self.postEventWithCallback(func)

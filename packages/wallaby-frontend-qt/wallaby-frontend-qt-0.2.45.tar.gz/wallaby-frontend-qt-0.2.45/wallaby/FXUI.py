# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# -*- coding: utf-8 -*-

import FX as FX
from twisted.python import log
from twisted.internet import defer, task
import sys, traceback, os, re, json
import socket
from platform import *

mineIcon = None
theirsIcon = None

configEditor = None

pLogo       = None
app         = None
mainWindow  = None

widgets  = []

def replaceValue(dct, val):
    val = FX.replaceValue(dct, val) 

    from qt_combat import QtGui, QtCore

    if len(val) > 0 and val[0] == ':':
        val = val.lower()
        val = QtGui.QPixmap(val)

    return val

def renderType(val, type, args, edit=False):
    val = FX.renderType(val, type, args, edit=edit, fct=replaceValue)

    from wallaby.qt_combat import QtCore
    if isinstance(val, QtCore.QPyNullVariant):
        val = "-"

    return val

def addShutdownCB(cb):
    shutdownCBs.append(cb)

def callShutdownCBs():
    for cb in shutdownCBs:
        cb()

def Property(function):
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probeFunc(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k,locals.get(k)) for k in keys))
            sys.settrace(None)
        return probeFunc
    sys.settrace(probeFunc)
    function()
    return property(**func_locals)

def imp(name):
    try:
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod
    except Exception as e:
        if True or not isinstance(e, ImportError):
            import traceback 
            traceback.print_exc(file=sys.stdout)
        return None

def compile(path):
    from wallaby.frontends.qt.compile import compile
    for p in path:
        compile(p)

def info(*msg):
    log.msg(toMessage("INFO" ,msg), logLevel=INFO)
    
def warn(*msg):    
    log.msg(toMessage("WARNING" ,msg), logLevel=WARN)
        
def crit(*msg):    
    log.err(toMessage("CRITICAL" ,msg), logLevel=CRIT)
        
def debug(*msg):    
    print toMessage("DEBUG", msg) #TODO: remove
    if not logDebug:
        return

    log.msg(toMessage("DEBUG" , msg), logLevel=DEBUG)
    
def trace(*params):
    if not logTrace:
        return

    log.msg(toMessage("TRACE" , params), logLevel=TRACE)
    
    type, value, trace = sys.exc_info()   
    stack = traceback.extract_stack()
    call  = stack[len(stack)-2]
    msg   = "FILE: " + call[0] + "  LINE: " + str(call[1])  
    log.msg(msg, logLevel=TRACE)

#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Converts a QKeyEvent to a standardized "name".
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from wallaby.qt_combat import *

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------
 
# Mapping from PyQt keypad key names to Pyface key names.
keypad_map = {
    QtCore.Qt.Key_Enter:     'Enter',
    QtCore.Qt.Key_0:         'Numpad 0',
    QtCore.Qt.Key_1:         'Numpad 1',
    QtCore.Qt.Key_2:         'Numpad 2',
    QtCore.Qt.Key_3:         'Numpad 3',
    QtCore.Qt.Key_4:         'Numpad 4',
    QtCore.Qt.Key_5:         'Numpad 5',
    QtCore.Qt.Key_6:         'Numpad 6',
    QtCore.Qt.Key_7:         'Numpad 7',
    QtCore.Qt.Key_8:         'Numpad 8',
    QtCore.Qt.Key_9:         'Numpad 9',
    QtCore.Qt.Key_Asterisk:  'Multiply',
    QtCore.Qt.Key_Plus:      'Add',
    QtCore.Qt.Key_Comma:     'Separator',
    QtCore.Qt.Key_Minus:     'Subtract',
    QtCore.Qt.Key_Period:    'Decimal',
    QtCore.Qt.Key_Slash:     'Divide'
}
 
# Mapping from PyQt non-keypad key names to Pyface key names.
key_map = {
    QtCore.Qt.Key_0:         '0',
    QtCore.Qt.Key_1:         '1',
    QtCore.Qt.Key_2:         '2',
    QtCore.Qt.Key_3:         '3',
    QtCore.Qt.Key_4:         '4',
    QtCore.Qt.Key_5:         '5',
    QtCore.Qt.Key_6:         '6',
    QtCore.Qt.Key_7:         '7',
    QtCore.Qt.Key_8:         '8',
    QtCore.Qt.Key_9:         '9',
    QtCore.Qt.Key_A:         'A',
    QtCore.Qt.Key_B:         'B',
    QtCore.Qt.Key_C:         'C',
    QtCore.Qt.Key_D:         'D',
    QtCore.Qt.Key_E:         'E',
    QtCore.Qt.Key_F:         'F',
    QtCore.Qt.Key_G:         'G',
    QtCore.Qt.Key_H:         'H',
    QtCore.Qt.Key_I:         'I',
    QtCore.Qt.Key_J:         'J',
    QtCore.Qt.Key_K:         'K',
    QtCore.Qt.Key_L:         'L',
    QtCore.Qt.Key_M:         'M',
    QtCore.Qt.Key_N:         'N',
    QtCore.Qt.Key_O:         'O',
    QtCore.Qt.Key_P:         'P',
    QtCore.Qt.Key_Q:         'Q',
    QtCore.Qt.Key_R:         'R',
    QtCore.Qt.Key_S:         'S',
    QtCore.Qt.Key_T:         'T',
    QtCore.Qt.Key_U:         'U',
    QtCore.Qt.Key_V:         'V',
    QtCore.Qt.Key_W:         'W',
    QtCore.Qt.Key_X:         'X',
    QtCore.Qt.Key_Y:         'Y',
    QtCore.Qt.Key_Z:         'Z',
    QtCore.Qt.Key_Space:     'Space',
    QtCore.Qt.Key_Backspace: 'Backspace',
    QtCore.Qt.Key_Tab:       'Tab',
    QtCore.Qt.Key_Enter:     'Enter',
    QtCore.Qt.Key_Return:    'Return',
    QtCore.Qt.Key_Escape:    'Esc',
    QtCore.Qt.Key_Delete:    'Delete',
    QtCore.Qt.Key_Cancel:    'Cancel',
    QtCore.Qt.Key_Clear:     'Clear',
    QtCore.Qt.Key_Shift:     'Shift',
    QtCore.Qt.Key_Menu:      'Menu',
    QtCore.Qt.Key_Pause:     'Pause',
    QtCore.Qt.Key_PageUp:    'Page Up',
    QtCore.Qt.Key_PageDown:  'Page Down',
    QtCore.Qt.Key_End:       'End',
    QtCore.Qt.Key_Home:      'Home',
    QtCore.Qt.Key_Left:      'Left',
    QtCore.Qt.Key_Up:        'Up',
    QtCore.Qt.Key_Right:     'Right',
    QtCore.Qt.Key_Down:      'Down',
    QtCore.Qt.Key_Select:    'Select',
    QtCore.Qt.Key_Print:     'Print',
    QtCore.Qt.Key_Execute:   'Execute',
    QtCore.Qt.Key_Insert:    'Insert',
    QtCore.Qt.Key_Help:      'Help',
    QtCore.Qt.Key_F1:        'F1',
    QtCore.Qt.Key_F2:        'F2',
    QtCore.Qt.Key_F3:        'F3',
    QtCore.Qt.Key_F4:        'F4',
    QtCore.Qt.Key_F5:        'F5',
    QtCore.Qt.Key_F6:        'F6',
    QtCore.Qt.Key_F7:        'F7',
    QtCore.Qt.Key_F8:        'F8',
    QtCore.Qt.Key_F9:        'F9',
    QtCore.Qt.Key_F10:       'F10',
    QtCore.Qt.Key_F11:       'F11',
    QtCore.Qt.Key_F12:       'F12',
    QtCore.Qt.Key_F13:       'F13',
    QtCore.Qt.Key_F14:       'F14',
    QtCore.Qt.Key_F15:       'F15',
    QtCore.Qt.Key_F16:       'F16',
    QtCore.Qt.Key_F17:       'F17',
    QtCore.Qt.Key_F18:       'F18',
    QtCore.Qt.Key_F19:       'F19',
    QtCore.Qt.Key_F20:       'F20',
    QtCore.Qt.Key_F21:       'F21',
    QtCore.Qt.Key_F22:       'F22',
    QtCore.Qt.Key_F23:       'F23',
    QtCore.Qt.Key_F24:       'F24',
    QtCore.Qt.Key_NumLock:   'Num Lock',
    QtCore.Qt.Key_ScrollLock:'Scroll Lock'
}
 
#-------------------------------------------------------------------------------
#  Converts a keystroke event into a corresponding key name:
#-------------------------------------------------------------------------------
 
def key_event_to_name(event):
    """ Converts a keystroke event into a corresponding key name.
    """
    key_code = event.key()
    modifiers = event.modifiers()
    if modifiers & QtCore.Qt.KeypadModifier:
        key = keypad_map.get(key_code)
    else:
        key = None
    if key is None:
        key = key_map.get(key_code)
 
    name = ''
    if modifiers & QtCore.Qt.ControlModifier:
        name += 'Ctrl'
 
    if modifiers & QtCore.Qt.AltModifier:
        name += '-Alt' if name else 'Alt'
 
    if modifiers & QtCore.Qt.MetaModifier:
        name += '-Meta' if name else 'Meta'
 
    if modifiers & QtCore.Qt.ShiftModifier and ((name != '') or (key is not None and len(key) > 1)):
        name += '-Shift' if name else 'Shift'
 
    if key:
        if name:
            name += '-'
        name += key
    return name
    
#-------------------------------------------------------------------------------

def toMessage(prefix, list):
    msg = prefix
    for m in list:
        msg = msg + " " + str(m)
    return msg
    
def deferredSleep(seconds):
    d = defer.Deferred()

    from twisted.internet import reactor
    reactor.callLater(seconds, d.callback, seconds)
    return d

def splitPath(path):
    return path.split('.');

def deferredCall(*args):
    from twisted.internet import reactor
    return task.deferLater(reactor, 0, *args)

def icon():
    from wallaby.qt_combat import QtGui
    return QtGui.QIcon(logo())

def logo():
    global pLogo
    if pLogo: return pLogo

    from wallaby.qt_combat import QtGui

    _logo_16x16_xpm = [
    "16 16 75 1 ",
    "  c #DE0101",
    ". c #DF0101",
    "X c #E20101",
    "o c #E5180C",
    "O c #E61B0E",
    "+ c #E62417",
    "@ c #E72519",
    "# c #E7261A",
    "$ c #E72B1F",
    "% c #E73629",
    "& c #E83B31",
    "* c #EA4136",
    "= c #EA453A",
    "- c #EB4C42",
    "; c #EB4F46",
    ": c #EC4F46",
    "> c #EB5148",
    ", c #EB594E",
    "< c #EA5B52",
    "1 c #EC5E55",
    "2 c #EE635A",
    "3 c #ED655B",
    "4 c #EE665D",
    "5 c #EF665D",
    "6 c #ED6961",
    "7 c #EF746C",
    "8 c #F0766F",
    "9 c #F1837B",
    "0 c #F18881",
    "q c #F28982",
    "w c #F08C85",
    "e c #F18C86",
    "r c #F3938B",
    "t c #F39893",
    "y c #F39993",
    "u c #F49B95",
    "i c #F4A19B",
    "p c #F4A19D",
    "a c #F4A29C",
    "s c #F5A49F",
    "d c #F5A8A2",
    "f c #F5AAA6",
    "g c #F6ABA6",
    "h c #F6AAA7",
    "j c #F6AEAB",
    "k c #F6B4B0",
    "l c #F7B6B2",
    "z c #F8BBB7",
    "x c #F7BEBA",
    "c c #F8C5C3",
    "v c #F8C6C2",
    "b c #F9C6C3",
    "n c #F8C9C6",
    "m c #FACCC9",
    "M c #F9CECB",
    "N c #F9CFCC",
    "B c #FAD1CE",
    "V c #F9D2CF",
    "C c #F9D3D0",
    "Z c #FAD5D2",
    "A c #FBD8D5",
    "S c #F9DAD9",
    "D c #FCDAD9",
    "F c #FCDDDB",
    "G c #FBDEDC",
    "H c #FBDFDD",
    "J c #FCE6E5",
    "K c #FCE7E5",
    "L c #FDEAE8",
    "P c #FDEFED",
    "I c #FDEFEE",
    "U c #FDF0EE",
    "Y c #FEF4F4",
    "T c #FEFFFF",
    "R c gray100",
    "RRRRRRRRRRRRRRRR",
    "RRRRRRRH&aRRRRRR",
    "RRRRRRRR*X7RRRRR",
    "RRRRRRRRwuRRRRRR",
    "RRRRRRRw=fSRRRRR",
    "RRRRRRM$rt3RRRRR",
    "RRRRRRf9vAdHRRRR",
    "RRRRRRR%3luRRRRR",
    "RHRRRRf X0<RRRRR",
    "Ra6nA<  o3wRRRRR",
    "RRk>@+;+z7BRRRRR",
    "RRRRRRc;R93RRRRR",
    "RRRRRRMoPJaxJRRR",
    "RRRRRRB aRH;BRRR",
    "RRRRRRU,cRYjPRRR",
    "RRRRRRRMLRRRRRRR" ]
    
    pLogo = QtGui.QPixmap(_logo_16x16_xpm)
    return pLogo

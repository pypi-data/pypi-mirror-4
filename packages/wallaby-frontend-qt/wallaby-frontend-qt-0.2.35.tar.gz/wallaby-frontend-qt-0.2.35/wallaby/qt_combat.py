#!/usr/bin/env python
# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.


from __future__ import with_statement
from __future__ import division

_TRY_PYSIDE = False

try:
    if not _TRY_PYSIDE:
        raise ImportError()
    import PySide.QtCore as _QtCore
    import PySide.QtGui as _QtGui
    import PySide.QtDesigner as _QtDesigner
    QtCore = _QtCore
    QtGui = _QtGui
    QtDesigner = _QtDesigner
    USES_PYSIDE = True
except ImportError:
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    import PyQt4.QtCore as _QtCore
    import PyQt4.QtGui as _QtGui
    import PyQt4.QtDesigner as _QtDesigner
    QtCore = _QtCore
    QtGui = _QtGui
    QtDesigner = _QtDesigner
    USES_PYSIDE = False


def _pyside_import_module(moduleName):
    pyside = __import__('PySide', globals(), locals(), [moduleName], -1)
    return getattr(pyside, moduleName)


def _pyqt4_import_module(moduleName):
    pyside = __import__('PyQt4', globals(), locals(), [moduleName], -1)
    return getattr(pyside, moduleName)


if USES_PYSIDE:
    import_module = _pyside_import_module

    Signal = QtCore.Signal
    Slot = QtCore.Slot
    Property = QtCore.Property
else:
    import_module = _pyqt4_import_module

    Signal = QtCore.pyqtSignal
    Slot = QtCore.pyqtSlot
    Property = QtCore.pyqtProperty


if __name__ == "__main__":
    pass

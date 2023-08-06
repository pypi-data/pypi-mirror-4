# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

class ComboBoxDelegate(QtGui.QItemDelegate):
    def __init__(self, parent, idx):
        QtGui.QItemDelegate.__init__(self, parent)
    def _commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)
        editor.deregister(True)

    def createEditor(self, parent, options, index):
        from wallaby.frontends.qt.widgets.combo.comboBox import ComboBox
        editor = ComboBox(parent)
        editor.activated.connect(self._commitAndCloseEditor)
        editor.setObjectName(parent.parent().objectName() + unicode(index.column()))
        return editor

    def setEditorData(self, editor, index):
        print "Set Data"
        FX.mainWindow.configure(onlyNew=True)
        pass

    def setModelData(self, editor, model, index):
        print "Set Modeldata"
        pass

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

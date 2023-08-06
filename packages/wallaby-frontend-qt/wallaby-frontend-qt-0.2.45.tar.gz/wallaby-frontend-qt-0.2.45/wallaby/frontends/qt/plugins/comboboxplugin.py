# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FXUI as FXUI

from wallaby.qt_combat import *

from wallaby.frontends.qt.widgets.combo.comboBox import ComboBox

#============================================================================#
# The group name in designer widgetbox                                       #
#----------------------------------------------------------------------------#
DESIGNER_GROUP_NAME = "wallaby@fX"

#============================================================================#
# Plugin for CTLiveView                                                      #
#----------------------------------------------------------------------------#
class ComboBoxPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent=None):
        super(ComboBoxPlugin, self).__init__(parent)

        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return
        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return False

    def icon(self):
        return FXUI.icon()

    def domXml(self):
        return '<widget class="ComboBox" name="ComboBox">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "wallaby.frontends.qt.widgets.combo.comboBox"

    def name(self):
        return "ComboBox"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ComboBox(parent)

# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FXUI as FXUI

from wallaby.qt_combat import *

from wallaby.frontends.qt.widgets.containers.stacked import Stacked

#============================================================================#
# The group name in designer widgetbox                                       #
#----------------------------------------------------------------------------#
DESIGNER_GROUP_NAME = "wallabyContainers@fX"

#============================================================================#
# Plugin for CTLiveView                                                      #
#----------------------------------------------------------------------------#
class StackedPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent=None):
        super(StackedPlugin, self).__init__(parent)

        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return
        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def isContainer(self):
        return True

    def icon(self):
        return FXUI.icon()

    def domXml(self):
        return '<widget class="Stacked" name="stacked">\n</widget>\n'
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "wallaby.frontends.qt.widgets.containers.stacked"

    def name(self):
        return "Stacked"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return Stacked(parent)

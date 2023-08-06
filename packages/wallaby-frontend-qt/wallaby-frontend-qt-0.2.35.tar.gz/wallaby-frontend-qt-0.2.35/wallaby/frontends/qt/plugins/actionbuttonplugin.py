# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FXUI as FXUI

from wallaby.qt_combat import *

from wallaby.frontends.qt.widgets.buttons.actionButton import ActionButton

#============================================================================#
# The group name in designer widgetbox                                       #
#----------------------------------------------------------------------------#
DESIGNER_GROUP_NAME = "wallaby@fX"

#============================================================================#
# Plugin for CTLiveView                                                      #
#----------------------------------------------------------------------------#
class ActionButtonPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent=None):
        super(ActionButtonPlugin, self).__init__(parent)

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
        return '<widget class="ActionButton" name="actionButton">\n</widget>\n'
#         return """
#  <ui language="c++" displayname="ActionButton">
#      <widget class="ActionButton" name="actionButton"/>
#      <customwidgets>
#          <customwidget>
#              <class>ActionButton</class>
#              <propertyspecifications>
#                  <stringpropertyspecification name="payload" notr="true" type="multiline"/>
#              </propertyspecifications>
#          </customwidget>
#      </customwidgets>
#  </ui>
#         """
    
    def group(self):
        return DESIGNER_GROUP_NAME
              
    def includeFile(self):
        return "wallaby.frontends.qt.widgets.buttons.actionButton"

    def name(self):
        return "ActionButton"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def createWidget(self, parent):
        return ActionButton(parent)

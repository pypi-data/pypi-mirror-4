# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

class Options:
    def __init__(self):
        self.server = "127.0.0.1"
        self.app = "$appname$"
        self.db = "$appname$"
        self.password = self.username = None
        self.fx = True
        self.debug = ""

import warnings
warnings.simplefilter('ignore')

import wallaby.apps.wallabyApp
wallaby.apps.wallabyApp.WallabyApp("$appname$", options=Options())

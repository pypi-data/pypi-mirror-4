#!/usr/bin/env python
# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import os, re, shutil, os.path, platform, sys, glob

from wallaby.qt_combat import *

def compile(path):
    #platform
    uname     = platform.uname()
    
    if re.search("2.6", sys.version):
        pythonpath  = '/System/Library/Frameworks/Python.framework/Versions/2.6/bin/'
    elif re.search("2.7", sys.version):
        # Default install path for python.org python 2.7 dmg on OSX 10.6
        if os.path.isdir("/Library/Frameworks/Python.framework/Versions/2.7/bin/"):
            pythonpath = '/Library/Frameworks/Python.framework/Versions/2.7/bin/'
        else:
            pythonpath  = '/System/Library/Frameworks/Python.framework/Versions/2.7/bin/'
    else:
        print 'No supported version of python found (2.6/2.7) != '+sys.version
        exit(1);
    
    if not USES_PYSIDE:
        uic = 'pyuic4'
        rcc = 'pyrcc4'
    
        if os.path.isfile('/usr/local/bin/pyrcc4'):
            pythonpath = '/usr/local/bin/'

        if os.path.isfile('/usr/bin/pyrcc4'):
            pythonpath = '/usr/bin/'
    else:
        uic = 'pyside-uic'
        rcc = 'pyside-rcc'
    
        if os.path.isfile('/usr/local/bin/pyside-rcc'):
            pythonpath = '/usr/local/bin/'

        if os.path.isfile('/usr/bin/pyside-rcc'):
            pythonpath = '/usr/bin/'

    if not os.path.exists(pythonpath+uic):
        pythonpath = ''

    for file in glob.glob(path + "/*.ui"):    
        root, file = os.path.split(file)
        basename, ext = os.path.splitext(file)

        src = os.path.join(root, file)
        dst = os.path.join(root, 'UI_' + basename + '.py')

        if not os.path.exists(dst) or os.stat(src).st_mtime > os.stat(dst).st_mtime:
            print "translating", src, "->", dst
    
            #OSX
            if uname[0] in ('Darwin', 'Linux'):
                os.system(pythonpath+uic+' --from-imports '+src+' > '+dst)
            #Windows
            elif uname[0] == 'Windows':
                os.system('pyuic4.bat --from-imports '+src+' > '+dst)

    for file in glob.glob(path + "/*.qrc"):
        root, file = os.path.split(file)
        basename, ext = os.path.splitext(file)
        src = os.path.join(root, file)
        dst = os.path.join(root, basename + '_rc.py')
    
        if not os.path.exists(dst) or os.stat(src).st_mtime > os.stat(dst).st_mtime:
            print "translating", src, "->", dst
    
            #OSX
            if uname[0] in ('Darwin', 'Linux'):
                os.system(pythonpath+rcc+' '+src+' > '+dst)
            #Windows
            elif uname[0] == 'Windows':
                os.system('pyrcc4.exe '+src+' > '+dst)

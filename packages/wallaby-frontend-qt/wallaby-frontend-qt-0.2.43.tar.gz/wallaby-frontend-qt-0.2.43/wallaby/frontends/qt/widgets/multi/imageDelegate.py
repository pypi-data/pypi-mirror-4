# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

class ProgressDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        obj = index.data(QtCore.Qt.DisplayRole)

        rect = option.rect

        painter.save()

        if not isinstance(obj, (float, int)):
            painter.drawText(rect, QtCore.Qt.AlignCenter, unicode(obj))
            painter.restore()
            return

        w = float(rect.width()-10)/100.0*float(obj)
        if w < 1.0: w = 1.0 
        if w > rect.width()-10: w = rect.width()-10

        margin = rect.height()/4
        painter.fillRect(rect.x()+5, rect.y()+margin, w, rect.height() - 2*margin, QtGui.QColor(0, 128, 128, 128))
        painter.drawText(rect, QtCore.Qt.AlignCenter, unicode(int(obj)) + u" %")
        painter.restore()

class ImageDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent)

    def paint(self, painter, option, index):
        # obj = index.data(QtCore.Qt.DisplayRole).toPyObject()
        obj = index.data(QtCore.Qt.DisplayRole)

        rect = option.rect
        # rect.adjust(rect.width()/3, 0, -rect.width()/3, 0)

        lst = []
        isList = False

        painter.save()

        maxHeight = 0

        if isinstance(obj, list):
            lst = []
            isList = True
            for o in obj:
                if isinstance(o, QtGui.QPixmap):
                    if o.height() > maxHeight: maxHeight = o.height()
                    lst.append(o)

        elif isinstance(obj, QtGui.QPixmap):
            lst.append(obj)
            if obj.height() > maxHeight: maxHeight = obj.height()
        else:
            if isinstance(obj, QtCore.QPyNullVariant): obj = "-"
            painter.drawText(rect, QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter | QtCore.Qt.TextWordWrap, unicode(obj))
            painter.restore()
            return

        if maxHeight == 0: 
            painter.restore()
            return

        if len(lst) == 0: 
            painter.restore()
            return

        if maxHeight > rect.height():
            ratio = float(rect.height()-2)/float(maxHeight)
        else:
            ratio = 1.0

        dx = lst[0].width()
        width = dx*len(lst)

        if not isList and width > rect.width():
            ratio2 = float(rect.width()-2)/float(width)
            if ratio2 < ratio: ratio = ratio2

        dx = int(ratio*float(dx))

        x = rect.x() # + rect.width()/2.0-width/2.0
        y = rect.y()
        i = 0

        lmargin = rect.height()/4

        while x < rect.x():
            i += 1
            x += dx

        while i < len(lst) and x + dx < rect.x() + rect.width():
            pixmap = lst[i]
            if pixmap.width() == 0 or pixmap.height() == 0: 
                i += 1
                continue
            if ratio < 1.0:
                pixmap = pixmap.scaled(QtCore.QSize(int(float(pixmap.width())*ratio), int(float(pixmap.height())*ratio)), QtCore.Qt.KeepAspectRatio)

            if not isList:
                painter.drawPixmap(x + option.rect.width()/2-pixmap.width()/2, y+option.rect.height()/2-pixmap.height()/2, pixmap)
            else:
                painter.drawPixmap(x, y, pixmap)

            if i < len(lst)-1:
                painter.drawLine(x+dx, y+lmargin, x+dx, y+rect.height()-lmargin)

            x += dx
            i += 1

        painter.restore()

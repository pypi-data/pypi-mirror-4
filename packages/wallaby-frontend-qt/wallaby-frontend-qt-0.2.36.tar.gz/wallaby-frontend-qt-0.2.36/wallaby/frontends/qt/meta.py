# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from functools import wraps, partial
#from sets import Set

import wallaby.FX as FX

from wallaby.qt_combat import *

class APIProperty(object):
    def __init__(self, type, extended=False, doc=u"", example=u"", default=None, readOnly=False):
        self.type = type
        self.extended = extended
        self.doc = doc
        self.example = example
        self.default = default
        self.readOnly = readOnly

try:
    MetaQObject = type(QtCore.QObject)

    def setObjectName(self, name, base=None):
        if base is not None: base.setObjectName(self, name)
        from wallaby.frontends.qt.widgets.baseWidget import BaseWidget
        BaseWidget.registerConfigViewer(self)
    
    def repartial(func, *parameters, **kparms):
        @wraps(func)
        def wrapped(self, *args, **kw):
            kw.update(kparms)
            return func(self, *(args + parameters), **kw)
        return wrapped
    
    class QWallabyMeta(MetaQObject):
        @staticmethod
        def _recursivePropertyDiscovery(cls=None, bases=None, dict=None):
            if cls != None:
                _bases = cls.__bases__
                _dict = cls.__dict__
            else:
                _bases = bases
                _dict = dict

            properties = {}

            for base in _bases:
                dict = QWallabyMeta._recursivePropertyDiscovery(cls=base)
                for k,v in dict.iteritems():
                    properties[k]=v

            for k,v in _dict.iteritems():
                if isinstance(v, property):
                    properties[k]=(v,_dict['wallabyProperties'][k])

            return properties

        def __new__(mcs, name, bases, dict):
            from wallaby.frontends.qt.widgets.baseWidget import BaseWidget
            newdict = {}
            properties = {}

            properties = QWallabyMeta._recursivePropertyDiscovery(bases=bases,dict=dict)
            for k,(v,p) in properties.iteritems():
                dict[k]=v
                properties[k]=p

            dict["wallabyType"] = APIProperty("string")

            for k in dict:
                if isinstance(dict[k], APIProperty):
                    prop = dict[k]
                    var = k[0:1].upper() + k[1:]
                    properties[k] = prop
    
                    newdict['set' + var] = repartial(BaseWidget.setConfig, key=k, type=prop.type)
                    newdict['get' + var] = repartial(BaseWidget.getConfig, key=k, type=prop.type)
                    newdict['reset' + var] = repartial(BaseWidget.resetConfig, key=k, type=prop.type)

                    newdict[k] = property(fget=newdict['get' + var], fset=newdict['set' + var])

            dict["template"] = Property("QString", fget   = repartial(BaseWidget.getWallabyTemplate),
                                                   fset   = repartial(BaseWidget.setWallabyTemplate),
                                                   freset = repartial(BaseWidget.resetWallabyTemplate))

            dict['wallabyProperties'] = properties 
    
            dict['setObjectName'] = repartial(setObjectName, base=bases[0])

            for k, v in newdict.items():
                dict[k] = v

            cls = MetaQObject.__new__(mcs, name, bases, dict)
            return cls
except:
    pass

class Meta(object):
    @staticmethod
    def property(type, extended=False, doc=u"", example=u"", default=None, readOnly=False):
       return APIProperty(type, extended=extended, doc=doc, example=example, default=default, readOnly=readOnly)

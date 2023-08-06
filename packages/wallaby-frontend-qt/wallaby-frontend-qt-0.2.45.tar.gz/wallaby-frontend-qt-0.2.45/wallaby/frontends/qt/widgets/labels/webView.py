# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.payloadCallback import *

class WebView(QtWebKit.QWebView, BaseWidget, EnableLogic, ViewLogic, TriggeredPillowsLogic):
    __metaclass__ = QWallabyMeta

    markdown = Meta.property('bool')
    codeHighlight = Meta.property('bool')
    allowExternalLinks = Meta.property('bool', default=False)
    useValueAsUrl = Meta.property('bool', default=False)

    identifier = Meta.property('string')

    triggers = Meta.property("list", readOnly=True, default=["", "double-clicked"])

    def __init__(self, *args):
        QtWebKit.QWebView.__init__(self, *args)
        BaseWidget.__init__(self, QtWebKit.QWebView, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self._setText)
        TriggeredPillowsLogic.__init__(self)
        self.linkClicked.connect(self._linkActivated)

        self._backPeer = None
        self._forwardPeer = None
        self._reloadPeer = None

    def mouseDoubleClickEvent(self, e):
        self.trigger("double-clicked")

    def _linkActivated(self, url):
        link = unicode(url.toString())
        if link.startswith('wallaby://'):
            link = link.replace('wallaby://', '')
            args = None
            if '/' in link:
                args = link.split('/')
                _ = args.pop(0)
                link = args.pop(0)

                if len(args) == 1:
                    args = args[0]

            House.get(self.room).throw(link, args)
        else:
            if self.allowExternalLinks:
                self.load(url)
            else:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(link))

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)
        TriggeredPillowsLogic.deregister(self, remove)

        for peer in (self._backPeer, self._forwardPeer, self._reloadPeer):
            if peer: peer.destroy()

        self._backPeer = None
        self._forwardPeer = None
        self._reloadPeer = None

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)
        TriggeredPillowsLogic.register(self)

        self._backPeer = PayloadCallback(self.room, "WebViewer.In.Back", self._back)
        self._forwardPeer = PayloadCallback(self.room, "WebViewer.In.Forward", self._forward)
        self._reloadPeer = PayloadCallback(self.room, "WebViewer.In.Reload", self._reload)

    def _back(self, ident):
        if self.identifier is None or ident == self.identifier: 
            self.back() 

    def _forward(self, *args):
        if self.identifier is None or ident == self.identifier: 
            self.forward() 

    def _reload(self, *args):
        if self.identifier is None or ident == self.identifier: 
            self.reload() 

    def _setText(self, text):
        if self.useValueAsUrl:
            try:
                url = QtCore.QUrl(unicode(text))
                self.load(url) 
                return
            except: pass

        if self.markdown:
            import markdown
            if self.codeHighlight:
                text = markdown.markdown(text, ['fenced_code', 'codehilite'])
                prefix = """
<html><head>
<style type="text/css">
.hll { background-color: #ffffcc }
.c { color: #999988; font-style: italic } /* Comment */
.err { color: #a61717; background-color: #e3d2d2 } /* Error */
.k { color: #000000; font-weight: bold } /* Keyword */
.o { color: #000000; font-weight: bold } /* Operator */
.cm { color: #999988; font-style: italic } /* Comment.Multiline */
.cp { color: #999999; font-weight: bold; font-style: italic } /* Comment.Preproc */
.c1 { color: #999988; font-style: italic } /* Comment.Single */
.cs { color: #999999; font-weight: bold; font-style: italic } /* Comment.Special */
.gd { color: #000000; background-color: #ffdddd } /* Generic.Deleted */
.ge { color: #000000; font-style: italic } /* Generic.Emph */
.gr { color: #aa0000 } /* Generic.Error */
.gh { color: #999999 } /* Generic.Heading */
.gi { color: #000000; background-color: #ddffdd } /* Generic.Inserted */
.go { color: #888888 } /* Generic.Output */
.gp { color: #555555 } /* Generic.Prompt */
.gs { font-weight: bold } /* Generic.Strong */
.gu { color: #aaaaaa } /* Generic.Subheading */
.gt { color: #aa0000 } /* Generic.Traceback */
.kc { color: #000000; font-weight: bold } /* Keyword.Constant */
.kd { color: #000000; font-weight: bold } /* Keyword.Declaration */
.kn { color: #000000; font-weight: bold } /* Keyword.Namespace */
.kp { color: #000000; font-weight: bold } /* Keyword.Pseudo */
.kr { color: #000000; font-weight: bold } /* Keyword.Reserved */
.kt { color: #445588; font-weight: bold } /* Keyword.Type */
.m { color: #009999 } /* Literal.Number */
.s { color: #d01040 } /* Literal.String */
.na { color: #008080 } /* Name.Attribute */
.nb { color: #0086B3 } /* Name.Builtin */
.nc { color: #445588; font-weight: bold } /* Name.Class */
.no { color: #008080 } /* Name.Constant */
.nd { color: #3c5d5d; font-weight: bold } /* Name.Decorator */
.ni { color: #800080 } /* Name.Entity */
.ne { color: #990000; font-weight: bold } /* Name.Exception */
.nf { color: #990000; font-weight: bold } /* Name.Function */
.nl { color: #990000; font-weight: bold } /* Name.Label */
.nn { color: #555555 } /* Name.Namespace */
.nt { color: #000080 } /* Name.Tag */
.nv { color: #008080 } /* Name.Variable */
.ow { color: #000000; font-weight: bold } /* Operator.Word */
.w { color: #bbbbbb } /* Text.Whitespace */
.mf { color: #009999 } /* Literal.Number.Float */
.mh { color: #009999 } /* Literal.Number.Hex */
.mi { color: #009999 } /* Literal.Number.Integer */
.mo { color: #009999 } /* Literal.Number.Oct */
.sb { color: #d01040 } /* Literal.String.Backtick */
.sc { color: #d01040 } /* Literal.String.Char */
.sd { color: #d01040 } /* Literal.String.Doc */
.s2 { color: #d01040 } /* Literal.String.Double */
.se { color: #d01040 } /* Literal.String.Escape */
.sh { color: #d01040 } /* Literal.String.Heredoc */
.si { color: #d01040 } /* Literal.String.Interpol */
.sx { color: #d01040 } /* Literal.String.Other */
.sr { color: #009926 } /* Literal.String.Regex */
.s1 { color: #d01040 } /* Literal.String.Single */
.ss { color: #990073 } /* Literal.String.Symbol */
.bp { color: #999999 } /* Name.Builtin.Pseudo */
.vc { color: #008080 } /* Name.Variable.Class */
.vg { color: #008080 } /* Name.Variable.Global */
.vi { color: #008080 } /* Name.Variable.Instance */
.il { color: #009999 } /* Literal.Number.Integer.Long */
</style>
</head>
<body>
                """

                text = prefix + text + "</body></html>"
            else:
                text = markdown.markdown(text, ['fenced_code'])

        self.setHtml(text)
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)

# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX

from wallaby.qt_combat import *

from ..baseWidget import *
from ..logics import *

from wallaby.pf.peer.viewer import *

class Label(QtGui.QLabel, BaseWidget, EnableLogic, ViewLogic):
    __metaclass__ = QWallabyMeta

    markdown = Meta.property('bool')

    def __init__(self, *args):
        QtGui.QLabel.__init__(self, *args)
        BaseWidget.__init__(self, QtGui.QLabel, *args)
        EnableLogic.__init__(self)
        ViewLogic.__init__(self, Viewer, self._setText)

        self.linkActivated.connect(self._linkActivated)

    def _linkActivated(self, link):
        link = unicode(link)
        if link.startswith('wallaby://'):
            link = link.replace('wallaby://', '')
            args = None
            if '/' in link:
                args = link.split('/')
                link = args.pop(0)

                if len(args) == 1:
                    args = args[0]

            House.get(self.room).throw(link, args)
        else:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(link))

    def deregister(self, remove=False):
        EnableLogic.deregister(self, remove)
        ViewLogic.deregister(self, remove)

    def register(self):
        EnableLogic.register(self)
        ViewLogic.register(self)

    def _setText(self, text):
        if self.markdown:
            import markdown
            text = markdown.markdown(text)

        if self.textFormat() == QtCore.Qt.RichText:
            import re

            try:
                # remove windows line breaks
                text = text.replace('\r\n', '\n')

                # h4 font
                text = re.sub(r"====(.*?)====", r"<h4>\1</h4>", text)

                # h3 font
                text = re.sub(r"===(.*?)===", r"<h3>\1</h3>", text)

                # h2 font
                text = re.sub(r"==(.*?)==", r"<h2>\1</h2>", text)

                # bold font
                text = re.sub(r"'''(.*?)'''", r"<b>\1</b>", text)

                # italic font
                text = re.sub(r"''(.*?)''", r"<i>\1</i>", text)

                # links
                text = re.sub(r"\[\[(.*?)\|(.*?)\]\]", r"<a href='\1'>\2</a>", text)

                # lists
                text = re.sub(r"(^|\n)\*(.*?)", r"__LI__\2", text)
                text = re.sub(r"(__LI__.*?)(\n|$)", r"<ul>\1</ul>\2", text)
                text = re.sub(r"__LI__(.*?)(?=(__LI__)|(</ul>))", r"<li>\1</li>", text)

                # numbered lists
                text = re.sub(r"(^|\n)#(.*?)", r"__LI__\2", text)
                text = re.sub(r"(__LI__.*?)(\n|$)", r"<ol>\1</ol>\2", text)
                text = re.sub(r"__LI__(.*?)(?=(__LI__)|(</ol>))", r"<li>\1</li>", text)

                # code blocks
                text = re.sub(r"\n ", r"__CB__", text)
                text = re.sub(r"(__CB__.*?)(\n|$)", r"<pre><code>\1</code></pre>", text)

                # breaks
                text = text.replace('\n', '<br>')

                # code blocks new lines
                text = re.sub(r"__CB__", r"\n", text)

                print text
            except Exception as e: print e

        self.setText(text)

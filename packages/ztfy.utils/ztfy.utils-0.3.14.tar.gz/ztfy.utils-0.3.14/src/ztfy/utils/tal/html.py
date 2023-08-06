### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from zope.tales.interfaces import ITALESFunctionNamespace

# import local interfaces
from ztfy.utils.tal.interfaces import IHTMLTalesAPI

# import Zope3 packages
from zope.interface import implements

# import local packages
from ztfy.utils.html import htmlToText
from ztfy.utils.text import textToHTML, Renderer


class HTMLTalesAdapter(object):

    implements(IHTMLTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def renderer(self):
        return Renderer(self.context)

    def totext(self):
        if not self.context:
            return u''
        return htmlToText(self.context)

    def text(self):
        if not self.context:
            return u''
        return textToHTML(self.context, 'zope.source.plaintext')

    def stx(self):
        if not self.context:
            return u''
        return textToHTML(self.context, 'zope.source.stx')

    def rest(self):
        if not self.context:
            return u''
        return textToHTML(self.context, 'zope.source.rest')

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
from ztfy.utils.tal.interfaces import ITextStartTalesAPI, ITextOutputTalesAPI

# import Zope3 packages
from zope.i18n import translate
from zope.interface import implements

# import local packages
from ztfy.utils.text import textStart


class TextStartTalesAdapter(object):

    implements(ITextStartTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def __getattr__(self, attr):
        try:
            if attr.find(',') > 0:
                length, max = (int(x) for x in attr.split(','))
            else:
                length = int(attr)
                max = 0
            return textStart(self.context, length, max)
        except:
            return ''


class TextOutputTalesAdapter(object):

    implements(ITextOutputTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self.request = engine.vars['request']

    def js(self):
        return self.context.replace("'", "&#039;").replace("\n", "&#013;")

    def noquotes(self):
        return self.context.replace('"', '')

    def breaks(self):
        return self.context.replace('|', '\n')

    def translate(self):
        return translate(self.context, context=self.request)

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

# import local interfaces

# import Zope3 packages
from zope.component import createObject, queryMultiAdapter

# import local packages
from ztfy.utils.request import getRequest


def textStart(text, length, max=0):
    """Get first words of given text with maximum given length
    
    If @max is specified, text is shortened only if remaining text is longer than @max
    
    @param text: initial text
    @param length: maximum length of resulting text
    @param max: if > 0, @text is shortened only if remaining text is longer than max
    """
    result = text or ''
    if length > len(result):
        return result
    index = length - 1
    text_length = len(result)
    while (index > 0) and (result[index] != ' '):
        index -= 1
    if (index > 0) and (text_length > index + max):
        return result[:index] + '&#133;'
    return text


def textToHTML(text, renderer='zope.source.plaintext', request=None):
    if request is None:
        request = getRequest()
    formatter = createObject(renderer, text)
    renderer = queryMultiAdapter((formatter, request), name=u'')
    return renderer.render()


class Renderer(object):

    def __init__(self, context):
        self.context = context

    def render(self, renderer, request=None):
        if not self.context:
            return u''
        return textToHTML(self.context, renderer, request)

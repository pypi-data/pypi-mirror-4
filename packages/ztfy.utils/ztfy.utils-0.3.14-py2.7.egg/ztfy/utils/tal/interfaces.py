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
from zope.interface import Interface

# import local packages


class ITextStartTalesAPI(Interface):
    """'start' TALES namespace interface"""

    def __getattr__(attr):
        """Get first characters of adapted text, without cutting words"""


class ITextOutputTalesAPI(Interface):
    """'text' TALES namespace interface"""

    def js():
        """Convert adapted text to a JavaScript compatible output"""

    def noquotes():
        """Remove double quotes from adapted text"""

    def breaks():
        """Replace '|' by newlines in adapted text"""

    def translate():
        """Use I18n translation of given text"""


class IHTMLTalesAPI(Interface):
    """'html' TALES namespace interface"""

    def renderer():
        """Get text to HTML renderer"""

    def totext():
        """Convert adapted HTML content to text"""

    def text():
        """Convert adapted text to HTML"""

    def stx():
        """Convert adapted StructuredText to HTML"""

    def rest():
        """Convert adapted reStructuredText to HTML"""


class IRequestDataTalesAPI(Interface):
    """Request 'data' TALES namespace interface"""

    def __getattr__(attr):
        """Get request data for given attribute"""


class ISessionDataTalesAPI(Interface):
    """Session data TALES namespace interface"""

    def __getattr__(attr):
        """Get session data for given app and key"""

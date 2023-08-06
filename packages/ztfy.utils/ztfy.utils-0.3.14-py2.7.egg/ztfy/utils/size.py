### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.i18n import translate

# import local packages
from ztfy.utils.request import queryRequest

from ztfy.utils import _


def getHumanSize(value, request=None):
    """Convert given bytes value in human readable format"""
    if request is None:
        request = queryRequest()
    if value < 1024:
        return translate(_("%d bytes"), context=request) % value
    value = value / 1024.0
    if value < 1024:
        return translate(_("%.1f Kb"), context=request) % value
    value = value / 1024.0
    if value < 1024:
        return translate(_("%.2f Mb"), context=request) % value
    value = value / 1024.0
    return translate(_("%.3f Gb"), context=request) % value

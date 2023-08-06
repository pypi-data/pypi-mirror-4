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
import pytz

# import Zope3 interfaces
from zope.interface.common.idatetime import ITZInfo
from zope.publisher.interfaces.browser import IBrowserRequest

# import local interfaces
from ztfy.utils.timezone.interfaces import IServerTimezone

# import Zope3 packages
from zope.component import adapter, queryUtility
from zope.interface import implementer

# import local packages


GMT = pytz.timezone('GMT')
_tz = pytz.timezone('Europe/Paris')
tz = _tz

@implementer(ITZInfo)
@adapter(IBrowserRequest)
def tzinfo(request=None):
    util = queryUtility(IServerTimezone)
    if util is not None:
        return pytz.timezone(util.timezone)
    return GMT


def tztime(value):
    if not value:
        return None
    if not value.tzinfo:
        value = GMT.localize(value)
    return value.astimezone(tzinfo())


def gmtime(value):
    if not value:
        return None
    if not value.tzinfo:
        value = GMT.localize(value)
    return value.astimezone(GMT)

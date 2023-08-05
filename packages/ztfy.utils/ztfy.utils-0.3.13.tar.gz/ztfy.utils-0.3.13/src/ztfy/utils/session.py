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
from zope.session.interfaces import ISession

# import local interfaces

# import Zope3 packages

# import local packages
from security import unproxied


def getData(request, app, key, default=None):
    """Get data associated with a given session"""
    session = ISession(request)[app]
    return session.get(key, default)

getSessionData = getData


def setData(request, app, key, value):
    """Set data associated to a given session"""
    session = ISession(request)[app]
    session[key] = unproxied(value)

setSessionData = setData

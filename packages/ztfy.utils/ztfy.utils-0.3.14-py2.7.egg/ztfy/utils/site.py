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
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.utils.interfaces import INewSiteManagerEvent

# import Zope3 packages
from zope.component import getUtility
from zope.interface import implements
from zope.location import locate

# import local packages


class NewSiteManagerEvent(object):
    """Event notified when a new site manager is created"""

    implements(INewSiteManagerEvent)

    def __init__(self, obj):
        self.object = obj


def locateAndRegister(contained, parent, key, intids=None):
    locate(contained, parent)
    if intids is None:
        intids = getUtility(IIntIds)
    intids.register(contained)
    parent[key] = contained

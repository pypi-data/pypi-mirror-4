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
from persistent import Persistent

# import Zope3 interfaces

# import local interfaces
from ztfy.utils.timezone.interfaces import IServerTimezone

# import Zope3 packages
from zope.container.contained import Contained
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages


class ServerTimezoneUtility(Persistent, Contained):

    implements(IServerTimezone)

    timezone = FieldProperty(IServerTimezone['timezone'])

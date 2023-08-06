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
from ztfy.skin.interfaces import IPropertiesMenuTarget
from ztfy.utils.interfaces import IZEOConnection

# import Zope3 packages
from z3c.form import field
from zope.interface import implements

# import local packages
from ztfy.skin.form import EditForm

from ztfy.utils import _


class ZEOConnectionEditForm(EditForm):
    """Sequential ID utility edit form"""

    implements(IPropertiesMenuTarget)

    legend = _("ZEO connection properties")

    fields = field.Fields(IZEOConnection)
    autocomplete = 'off'

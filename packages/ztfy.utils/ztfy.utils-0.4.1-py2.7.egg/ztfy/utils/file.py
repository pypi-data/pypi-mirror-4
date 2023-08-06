### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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
from z3c.form.interfaces import IFileWidget
from zope.schema.interfaces import IBytes

# import local interfaces

# import Zope3 packages
from z3c.form.converter import FileUploadDataConverter as BaseDataConverter
from zope.component import adapts

# import local packages


class FileUploadDataConverter(BaseDataConverter):

    adapts(IBytes, IFileWidget)

    def toWidgetValue(self, value):
        return value or ''

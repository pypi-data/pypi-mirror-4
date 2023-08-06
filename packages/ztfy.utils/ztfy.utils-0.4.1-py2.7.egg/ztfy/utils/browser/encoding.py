### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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
from z3c.form.interfaces import ISelectWidget, IFieldWidget
from zope.publisher.interfaces.browser import IBrowserRequest

# import local interfaces

# import Zope3 packages
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer, implementsOnly

# import local packages
from ztfy.utils.encoding import IEncodingField

from ztfy.utils import _


class IEncodingSelectWidget(ISelectWidget):
    """ENcoding select widget interface"""


class EncodingSelectWidget(SelectWidget):
    """Encoding select widget"""

    implementsOnly(IEncodingSelectWidget)

    noValueMessage = _("-- automatic selection --")


@adapter(IEncodingField, IBrowserRequest)
@implementer(IFieldWidget)
def EncodingSelectFieldWidget(field, request):
    """IFieldWidget factory for IEncodingSelectWidget"""
    return FieldWidget(field, EncodingSelectWidget(request))

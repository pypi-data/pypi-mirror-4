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
from z3c.form.interfaces import ITextWidget, IFieldWidget, IFormLayer

# import local interfaces
from ztfy.utils.schema import IColorField

# import Zope3 packages
from z3c.form.browser.text import TextWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer, implementsOnly

# import local packages
from ztfy.jqueryui import jquery_colorpicker


class IColorWidget(ITextWidget):
    """Color widget interface"""


class ColorWidget(TextWidget):
    """Color widget"""

    implementsOnly(IColorWidget)

    def update(self):
        TextWidget.update(self)
        jquery_colorpicker.need()


@adapter(IColorField, IFormLayer)
@implementer(IFieldWidget)
def ColorFieldWidgetFactory(field, request):
    """IColorField widget factory"""
    return FieldWidget(field, ColorWidget(request))

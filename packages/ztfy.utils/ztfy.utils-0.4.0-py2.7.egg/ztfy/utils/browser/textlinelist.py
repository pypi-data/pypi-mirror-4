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
from z3c.form.interfaces import IWidget, IFieldWidget, ITextWidget, IFormLayer

# import local interfaces
from ztfy.utils.schema import ITextLineListField

# import Zope3 packages
from z3c.form.browser.text import TextWidget
from z3c.form.converter import SequenceDataConverter
from z3c.form.widget import FieldWidget
from zope.component import adapter, adapts
from zope.interface import implementer, implementsOnly

# import local packages
from ztfy.jqueryui import jquery_multiselect


class ITextLineListWidget(ITextWidget):
    """TextLineList widget interface"""


class TextLineListDataConverter(SequenceDataConverter):
    """TextLineList field data converter"""

    adapts(ITextLineListField, IWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return []
        return '|'.join(value)

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value
        return value.split('|')


class TextLineListWidget(TextWidget):
    """TextLineList field widget"""

    implementsOnly(ITextLineListWidget)

    def render(self):
        jquery_multiselect.need()
        return super(TextLineListWidget, self).render()


@adapter(ITextLineListField, IFormLayer)
@implementer(IFieldWidget)
def TextLineListFieldWidgetFactory(field, request):
    return FieldWidget(field, TextLineListWidget(request))

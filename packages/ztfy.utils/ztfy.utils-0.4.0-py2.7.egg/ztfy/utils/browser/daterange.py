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
from z3c.form.interfaces import IMultiWidget, IFieldWidget, NO_VALUE

# import local interfaces
from ztfy.skin.layer import IZTFYBrowserLayer
from ztfy.utils.schema import IDatesRangeField

# import Zope3 packages
from z3c.form.browser.widget import HTMLFormElement
from z3c.form.converter import SequenceDataConverter, FormatterValidationError
from z3c.form.widget import FieldWidget, Widget
from zope.component import adapter, adapts
from zope.interface import implementer, implements
from zope.i18n.format import DateTimeParseError

# import local packages
from ztfy.jqueryui import jquery_datetime


class IDatesRangeWidget(IMultiWidget):
    """Dates range widget interface"""


class DatesRangeDataConverter(SequenceDataConverter):
    """Dates range data converter"""

    adapts(IDatesRangeField, IDatesRangeWidget)

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return (u'', u'')
        locale = self.widget.request.locale
        formatter = locale.dates.getFormatter('date', 'short')
        return (formatter.format(value[0]) if value[0] else None,
                formatter.format(value[1]) if value[1] else None)

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value
        try:
            locale = self.widget.request.locale
            formatter = locale.dates.getFormatter('date', 'short')
            return (formatter.parse(value[0]) if value[0] else None,
                    formatter.parse(value[1]) if value[1] else None)
        except DateTimeParseError, err:
            raise FormatterValidationError(err.args[0], value)


class DatesRangeWidget(HTMLFormElement, Widget):
    """Dates range widget"""

    implements(IDatesRangeWidget)

    @property
    def pattern(self):
        result = self.request.locale.dates.getFormatter('date', 'short').getPattern()
        return result.replace('dd', '%d').replace('MM', '%m').replace('yy', '%y')

    @property
    def begin_id(self):
        return '%s-begin' % self.id

    @property
    def begin_name(self):
        return '%s.begin' % self.name

    @property
    def begin_date(self):
        return (self.value[0] or '') if self.value else ''

    @property
    def end_id(self):
        return '%s-end' % self.id

    @property
    def end_name(self):
        return '%s.end' % self.name

    @property
    def end_date(self):
        return (self.value[1] or '') if self.value else ''

    def extract(self, default=NO_VALUE):
        begin_date = self.request.get(self.begin_name)
        end_date = self.request.get(self.end_name)
        return (begin_date, end_date)

    def render(self):
        result = super(DatesRangeWidget, self).render()
        if result:
            jquery_datetime.need()
        return result

@adapter(IDatesRangeField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def DatesRangeFieldWidgetFactory(field, request):
    """IDatesRangeField widget factory"""
    return FieldWidget(field, DatesRangeWidget(request))

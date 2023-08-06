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
import decimal
import string

# import Zope3 interfaces
from z3c.form.interfaces import IWidget
from zope.schema.interfaces import ITextLine, IDecimal, IList, ITuple

# import local interfaces

# import Zope3 packages
from z3c.form.converter import BaseDataConverter, FormatterValidationError
from zope.component import adapts
from zope.interface import implements
from zope.schema import TextLine, Decimal, List, Tuple
from zope.schema._bootstrapfields import InvalidValue

# import local packages

from ztfy.utils import _


class StringLine(TextLine):
    """String line field"""

    _type = str

    def fromUnicode(self, value):
        return str(value)


#
# Color field
#

class IColorField(ITextLine):
    """Marker interface for color fields"""


class ColorField(TextLine):
    """Color field"""

    implements(IColorField)

    def __init__(self, *args, **kw):
        super(ColorField, self).__init__(max_length=6, *args, **kw)

    def _validate(self, value):
        if len(value) not in (3, 6):
            raise InvalidValue, _("Color length must be 3 or 6 characters")
        for v in value:
            if v not in string.hexdigits:
                raise InvalidValue, _("Color value must contain only valid color codes (numbers or letters between 'A' end 'F')")
        super(ColorField, self)._validate(value)


#
# Pointed decimal field
#

class IDottedDecimalField(IDecimal):
    """Marker interface for dotted decimal fields"""


class DottedDecimalField(Decimal):
    """Dotted decimal field"""

    implements(IDottedDecimalField)


class DottedDecimalDataConverter(BaseDataConverter):
    """Dotted decimal field data converter"""

    adapts(IDottedDecimalField, IWidget)

    errorMessage = _('The entered value is not a valid decimal literal.')

    def __init__(self, field, widget):
        super(DottedDecimalDataConverter, self).__init__(field, widget)

    def toWidgetValue(self, value):
        if not value:
            return self.field.missing_value
        return str(value)

    def toFieldValue(self, value):
        if value is self.field.missing_value:
            return u''
        if not value:
            return None
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation:
            raise FormatterValidationError(self.errorMessage, value)


#
# Dates range field
#

class IDatesRangeField(ITuple):
    """Marker interface for dates range fields"""


class DatesRangeField(Tuple):
    """Dates range field"""

    implements(IDatesRangeField)

    def __init__(self, value_type=None, unique=False, **kw):
        super(DatesRangeField, self).__init__(value_type=None, unique=False,
                                              min_length=2, max_length=2, **kw)


#
# TextLine list field
#

class ITextLineListField(IList):
    """Marker interface for textline list field"""


class TextLineListField(List):
    """TextLine list field"""

    implements(ITextLineListField)

    def __init__(self, value_type=None, unique=False, **kw):
        super(TextLineListField, self).__init__(value_type=TextLine(), unique=True, **kw)

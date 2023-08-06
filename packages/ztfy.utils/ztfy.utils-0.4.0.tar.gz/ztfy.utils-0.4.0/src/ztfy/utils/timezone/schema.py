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
import pytz

# import Zope3 interfaces
from zope.schema.interfaces import IChoice, IVocabularyFactory

# import local interfaces

# import Zope3 packages
from zope.interface import implements, classProvides
from zope.schema import Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# import local packages


class TimezonesVocabulary(SimpleVocabulary):

    classProvides(IVocabularyFactory)

    def __init__(self, *args, **kw):
        terms = [SimpleTerm(t, t, t) for t in pytz.all_timezones]
        super(TimezonesVocabulary, self).__init__(terms)


class ITimezone(IChoice):
    """Marker interface for timezone field"""


class Timezone(Choice):
    """Timezone choice field"""

    implements(ITimezone)

    def __init__(self, **kw):
        if 'vocabulary' in kw:
            kw.pop('vocabulary')
        if 'default' not in kw:
            kw['default'] = u'GMT'
        super(Timezone, self).__init__(vocabulary='ZTFY timezones', **kw)

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
from datetime import datetime

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.datetime import parseDatetimetz
from zope.i18n import translate

# import local packages
from timezone import gmtime

from ztfy.utils import _


def unidate(value):
    """Get specified date converted to unicode ISO format
    
    Dates are always assumed to be stored in GMT timezone
    
    @param value: input date to convert to unicode
    @type value: date or datetime
    @return: input date converted to unicode
    @rtype: unicode
    """
    if value is not None:
        value = gmtime(value)
        return unicode(value.isoformat('T'), 'ascii')
    return None


def parsedate(value):
    """Get date specified in unicode ISO format to Python datetime object
    
    Dates are always assumed to be stored in GMT timezone
    
    @param value: unicode date to be parsed
    @type value: unicode
    @return: the specified value, converted to datetime
    @rtype: datetime
    """
    if value is not None:
        return gmtime(parseDatetimetz(value))
    return None


def datetodatetime(value):
    """Get datetime value converted from a date or datetime object
    
    @param value: a date or datetime value to convert
    @type value: date or datetime
    @return: input value converted to datetime
    @rtype: datetime
    """
    if type(value) is datetime:
        return value
    return datetime(value.year, value.month, value.day)


def getAge(value):
    """Get age of a given datetime (including timezone) compared to current datetime (in UTC)
    
    @param value: a datetime value, including timezone
    @type value: datetime
    @return: string representing value age
    @rtype: gettext translated string
    """
    now = gmtime(datetime.utcnow())
    delta = now - value
    if delta.days > 60:
        return translate(_("%d months ago")) % int(round(delta.days * 1.0 / 30))
    elif delta.days > 10:
        return translate(_("%d weeks ago")) % int(round(delta.days * 1.0 / 7))
    elif delta.days > 2:
        return translate(_("%d days ago")) % delta.days
    elif delta.days == 2:
        return translate(_("the day before yesterday"))
    elif delta.days == 1:
        return translate(_("yesterday"))
    else:
        hours = int(round(delta.seconds * 1.0 / 3600))
        if hours > 1:
            return translate(_("%d hours ago")) % hours
        elif delta.seconds > 300:
            return translate(_("%d minutes ago")) % int(round(delta.seconds * 1.0 / 60))
        else:
            return translate(_("less than 5 minutes ago"))


def getDuration(v1, v2=None):
    """Get delta between two dates"""
    if v2 is None:
        v2 = datetime.utcnow()
    assert isinstance(v1, datetime) and isinstance(v2, datetime)
    v1, v2 = min(v1, v2), max(v1, v2)
    delta = v2 - v1
    if delta.days > 60:
        return translate(_("%d months")) % int(round(delta.days * 1.0 / 30))
    elif delta.days > 10:
        return translate(_("%d weeks")) % int(round(delta.days * 1.0 / 7))
    elif delta.days >= 2:
        return translate(_("%d days")) % delta.days
    else:
        hours = int(round(delta.seconds * 1.0 / 3600))
        if delta.days == 1:
            return translate(_("%d day and %d hours")) % (delta.days, hours)
        else:
            if hours > 2:
                return translate(_("%d hours")) % hours
            else:
                minutes = int(round(delta.seconds * 1.0 / 60))
                if minutes > 2:
                    return translate(_("%d minutes")) % minutes
                else:
                    return translate(_("%d seconds")) % delta.seconds

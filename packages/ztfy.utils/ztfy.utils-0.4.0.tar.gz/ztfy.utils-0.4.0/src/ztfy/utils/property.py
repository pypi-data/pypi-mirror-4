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

# import Zope3 packages

# import local packages
from ztfy.utils.request import queryRequest, getRequestData, setRequestData
from ztfy.utils.session import getSessionData, setSessionData


class cached(object):
    """Custom property decorator to define a property or function
    which is calculated only once
       
    When applied on a function, caching is based on input arguments
    """

    def __init__(self, function):
        self._function = function
        self._cache = {}

    def __call__(self, *args):
        try:
            return self._cache[args]
        except KeyError:
            self._cache[args] = self._function(*args)
            return self._cache[args]

    def expire(self, *args):
        del self._cache[args]


class cached_property(object):
    """A read-only @property decorator that is only evaluated once. The value is cached
    on the object itself rather than the function or class; this should prevent
    memory leakage.
    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result


_marker = object()

class request_property(object):
    """Define a request cached property"""

    def __init__(self, fget, key=None):
        self.fget = fget
        if key is None:
            key = "%s.%s" % (fget.__module__, fget.__name__)
        self.key = key

    def __get__(self, obj, cls):
        if obj is None:
            return self
        request = queryRequest()
        data = getRequestData(self.key, request, _marker)
        if data is _marker:
            data = self.fget(obj)
            setRequestData(self.key, data, request)
        return data


class session_property(object):
    """Define a property for which computed value is stored into session"""

    def __init__(self, fget, app, key=None):
        self.fget = fget
        self.app = app
        if key is None:
            key = "%s.%s" % (fget.__module__, fget.__name__)
        self.key = key

    def __get__(self, obj, cls):
        if obj is None:
            return self
        request = queryRequest()
        data = getSessionData(request, self.app, self.key, _marker)
        if data is _marker:
            data = self.fget(obj)
            setSessionData(request, self.app, self.key, data)
        return data

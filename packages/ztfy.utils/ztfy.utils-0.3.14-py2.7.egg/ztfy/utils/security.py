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
from persistent.list import PersistentList
from persistent.dict import PersistentDict

# import Zope3 interfaces
from zope.authentication.interfaces import IAuthentication
from zope.pluggableauth.interfaces import IPrincipalInfo

# import local interfaces

# import Zope3 packages
from zc.set import Set
from zope.component import getUtility
from zope.deprecation.deprecation import deprecate
from zope.i18n import translate
from zope.interface import implements
from zope.security.proxy import removeSecurityProxy

# import local packages
from ztfy.utils.request import getRequest

from ztfy.utils import _


def unproxied(value):
    """Remove security proxies from given value ; if value is a list or dict, all elements are unproxied"""
    if isinstance(value, (list, PersistentList)):
        result = []
        for v in value:
            result.append(unproxied(v))
    elif isinstance(value, (dict, PersistentDict)):
        result = value.copy()
        for v in value:
            result[v] = unproxied(value[v])
    elif isinstance(value, (set, Set)):
        result = []
        for v in value:
            result.append(unproxied(v))
    else:
        result = removeSecurityProxy(value)
    return result


@deprecate("ztfy.utils.security.MissingPrincipal is deprecated. Use ztfy.security.search.MissingPrincipal class instead.")
class MissingPrincipal(object):

    implements(IPrincipalInfo)

    def __init__(self, id):
        self.id = id
        self.request = getRequest()

    @property
    def title(self):
        return translate(_("< missing principal %s >"), context=self.request) % self.id

    @property
    def description(self):
        return translate(_("This principal can't be found in any authentication utility..."), context=self.request)


@deprecate("ztfy.utils.security.getPrincipal is deprecated. Use ztfy.security.search.getPrincipal function instead.")
def getPrincipal(uid):
    principals = getUtility(IAuthentication)
    try:
        return principals.getPrincipal(uid)
    except:
        return MissingPrincipal(uid)

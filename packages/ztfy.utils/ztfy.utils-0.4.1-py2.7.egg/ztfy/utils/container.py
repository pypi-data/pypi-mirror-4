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
from ztfy.utils.unicode import translateString


def getContentName(container, base_name, translate=True, max_length=30):
    """Get a real name for a given base name and a container
    
    Target name will be suffixed with an index if base name already exists
    """
    if translate:
        base_name = translateString(base_name, escapeSlashes=True, spaces='-')
    if max_length:
        base_name = base_name[0:max_length]
    if base_name not in container:
        return base_name
    index = 2
    name = '%s-%02d' % (base_name, index)
    while name in container:
        index += 1
        name = '%s-%02d' % (base_name, index)
    return name

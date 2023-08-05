### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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
from zope.annotation.interfaces import IAnnotations
from zope.app.file.interfaces import IFile
from zope.catalog.interfaces import ICatalog
from zope.container.interfaces import IContainer
from zope.intid.interfaces import IIntIds

# import local interfaces

# import Zope3 packages
from zope.component import queryUtility, getAllUtilitiesRegisteredFor

# import local packages
from ztfy.utils import request as request_utils

from ztfy.utils import _


#
# IntIds utility functions
#

def getIntIdUtility(name='', request=None, context=None):
    """Look for a named IIntIds utility"""
    if request is None:
        request = request_utils.queryRequest()
    intids = None
    if request is not None:
        intids = request_utils.getRequestData('IntIdsUtility::' + name, request)
    if intids is None:
        intids = queryUtility(IIntIds, name, context=context)
        if (request is not None) and (intids is not None):
            request_utils.setRequestData('IntIdsUtility::' + name, intids, request)
    return intids


def getObjectId(object, intids_name='', request=None, context=None):
    """Look for an object Id as recorded by given IIntIds utility"""
    if object is None:
        return None
    if request is None:
        request = request_utils.queryRequest()
    intids = getIntIdUtility(intids_name, request, context)
    if intids is not None:
        return intids.queryId(object)
    return None


def getObject(id, intids_name='', request=None, context=None):
    """Look for an object recorded by given IIntIds utility and id"""
    if id is None:
        return None
    if request is None:
        request = request_utils.getRequest()
    intids = getIntIdUtility(intids_name, request, context)
    if intids is not None:
        return intids.queryObject(id)
    return None


#
# Catalog utility functions
#

def queryCatalog(name='', context=None):
    """Look for a registered catalog"""
    return queryUtility(ICatalog, name, context=context)


def indexObject(object, catalog_name='', index_name='', request=None, context=None):
    """Index object into a registered catalog"""
    if request is None:
        request = request_utils.getRequest()
    intids = getIntIdUtility('', request, context)
    if intids is not None:
        if ICatalog.providedBy(catalog_name):
            catalog = catalog_name
        else:
            catalog = queryCatalog(catalog_name, context)
        if catalog is not None:
            id = intids.register(object)
            if index_name:
                catalog[index_name].index_doc(id, object)
            else:
                catalog.index_doc(id, object)
            return True
    return False


def unindexObject(object, catalog_name='', index_name='', request=None, context=None):
    """Remove object from a registered catalog"""
    if request is None:
        request = request_utils.getRequest()
    id = getObjectId(object, '', request, context)
    if id is not None:
        if ICatalog.providedBy(catalog_name):
            catalog = catalog_name
        else:
            catalog = queryCatalog(catalog_name, context)
        if catalog is not None:
            if index_name:
                catalog[index_name].unindex_doc(id)
            else:
                catalog.unindex_doc(id)
            return True
    return False


def _indexObject(object, intids, catalogs):
    """Index object data into given set of catalogs"""
    id = intids.register(object)
    for catalog in catalogs:
        catalog.index_doc(id, object)

def _indexObjectValues(object, intids, catalogs):
    """Index object values into given set of catalogs"""
    container = IContainer(object, None)
    if container is not None:
        for subobject in container.values():
            _indexAllObject(subobject, intids, catalogs)

def _indexObjectAnnotations(object, intids, catalogs):
    """Index object annotations into given set of catalogs"""
    annotations = IAnnotations(object, None)
    if annotations is not None:
        keys = annotations.keys()
        for key in keys:
            _indexAllObject(annotations[key], intids, catalogs)
            file = IFile(annotations[key], None)
            if file is not None:
                _indexObject(file, intids, catalogs)

def _indexAllObject(object, intids, catalogs):
    """Index object, object values and annotations into given set of catalogs"""
    _indexObject(object, intids, catalogs)
    _indexObjectValues(object, intids, catalogs)
    _indexObjectAnnotations(object, intids, catalogs)

def indexAllObjectValues(object, context=None):
    """Reindex a whole container properties and contents (including annotations) into site's catalogs"""
    if context is None:
        context = object
    intids = queryUtility(IIntIds, context=context)
    if intids is not None:
        catalogs = getAllUtilitiesRegisteredFor(ICatalog, context)
        if catalogs:
            _indexAllObject(object, intids, catalogs)

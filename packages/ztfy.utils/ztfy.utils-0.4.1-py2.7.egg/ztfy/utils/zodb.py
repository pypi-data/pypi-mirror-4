### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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
from persistent import Persistent
from persistent.interfaces import IPersistent
from transaction.interfaces import ITransactionManager

# import Zope3 interfaces
from ZODB.interfaces import IConnection
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.utils.interfaces import IZEOConnection

# import Zope3 packages
from ZEO import ClientStorage
from ZODB import DB
from zope.component import adapter
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from zope.container.contained import Contained
from zope.interface import implementer, implements, classProvides
from zope.schema import getFieldNames
from zope.schema.fieldproperty import FieldProperty

# import local packages


class ZEOConnectionInfo(object):
    """ZEO connection info
    
    Provides a context manager which directly returns
    ZEO connection root
    """

    implements(IZEOConnection)

    _storage = None
    _db = None
    _connection = None

    server_name = FieldProperty(IZEOConnection['server_name'])
    server_port = FieldProperty(IZEOConnection['server_port'])
    storage = FieldProperty(IZEOConnection['storage'])
    username = FieldProperty(IZEOConnection['username'])
    password = FieldProperty(IZEOConnection['password'])
    server_realm = FieldProperty(IZEOConnection['server_realm'])
    blob_dir = FieldProperty(IZEOConnection['blob_dir'])
    shared_blob_dir = FieldProperty(IZEOConnection['shared_blob_dir'])

    def getSettings(self):
        result = {}
        for name in getFieldNames(IZEOConnection):
            result[name] = getattr(self, name)
        return result

    def update(self, settings):
        names = getFieldNames(IZEOConnection)
        for k, v in settings.items():
            if k in names:
                setattr(self, k, unicode(v) if isinstance(v, str) else v)

    def getConnection(self, wait=False, get_storage=False):
        """Get a tuple made of storage and DB connection for given settings"""
        storage = ClientStorage.ClientStorage((str(self.server_name), self.server_port),
                                              storage=self.storage,
                                              username=self.username or '',
                                              password=self.password or '',
                                              realm=self.server_realm,
                                              blob_dir=self.blob_dir,
                                              shared_blob_dir=self.shared_blob_dir,
                                              wait=wait)
        db = DB(storage)
        return (storage, db) if get_storage else db

    @property
    def connection(self):
        return self._connection

    # Context management methods
    def __enter__(self):
        self._storage, self._db = self.getConnection(get_storage=True)
        self._connection = self._db.open()
        return self._connection.root()

    def __exit__(self, exc_type, exc_value, traceback):
        if self._connection is not None:
            self._connection.close()
        if self._storage is not None:
            self._storage.close()


class ZEOConnectionUtility(ZEOConnectionInfo, Persistent, Contained):
    """Persistent ZEO connection settings utility"""


class ZEOConnectionVocabulary(UtilityVocabulary):
    """ZEO connections vocabulary"""

    classProvides(IVocabularyFactory)

    interface = IZEOConnection
    nameOnly = True


# IPersistent adapters copied from zc.twist package
# also register this for adapting from IConnection
@adapter(IPersistent)
@implementer(ITransactionManager)
def transactionManager(obj):
    conn = IConnection(obj) # typically this will be
                            # zope.app.keyreference.persistent.connectionOfPersistent
    try:
        return conn.transaction_manager
    except AttributeError:
        return conn._txn_mgr
        # or else we give up; who knows.  transaction_manager is the more
        # recent spelling.

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

# import Zope3 interfaces
from zope.component.interfaces import IObjectEvent

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Int, Password, Bool

# import local packages

from ztfy.utils import _


class INewSiteManagerEvent(IObjectEvent):
    """Event interface for new site manager event"""


#
# Generic list interface
#

class IListInfo(Interface):
    """Custom interface used to handle list-like components"""

    def count(self):
        """Get list items count"""

    def index(self):
        """Get position of the given item"""

    def __contains__(self, value):
        """Check if given value is in list"""

    def __getitem__(self, index):
        """Return item at given position"""

    def __iter__(self):
        """Iterator over list items"""


class IListWriter(Interface):
    """Writer interface for list-like components"""

    def append(self, value):
        """Append value to list"""

    def extend(self, values):
        """Extend list with given items"""

    def insert(self, index, value):
        """Insert item to given index"""

    def pop(self):
        """Pop item from list and returns it"""

    def remove(self, value):
        """Remove given item from list"""

    def reverse(self):
        """Sort list in reverse order"""

    def sort(self):
        """Sort list"""


class IList(IListInfo, IListWriter):
    """Marker interface for list-like components"""


#
# Generic dict interface
#

class IDictInfo(Interface):
    """Custom interface used to handle dict-like components"""

    def keys(self):
        """Get list of keys for the dict"""

    def has_key(self, key):
        """Check to know if dict includes the given key"""

    def get(self, key, default=None):
        """Get given key or default from dict"""

    def copy(self,):
        """Duplicate content of dict"""

    def __contains__(self, key):
        """Check if given key is in dict"""

    def __getitem__(self, key):
        """Get given key value from dict"""

    def __iter__(self):
        """Iterator over dictionnary keys"""


class IDictWriter(Interface):
    """Writer interface for dict-like components"""

    def clear(self):
        """Clear dict"""

    def update(self, b):
        """Update dict with given values"""

    def setdefault(self, key, failobj=None):
        """Create value for given key if missing"""

    def pop(self, key, *args):
        """Remove and return given key from dict"""

    def popitem(self, item):
        """Pop item from dict"""

    def __setitem__(self, key, value):
        """Update given key with given value"""

    def __delitem__(self, key):
        """Remove selected key from dict"""


class IDict(IDictInfo, IDictWriter):
    """Marker interface for dict-like components"""


#
# ZEO connection settings interface
#

class IZEOConnection(Interface):
    """ZEO connection settings interface"""

    server_name = TextLine(title=_("ZEO server name"),
                           description=_("Hostname of ZEO server"),
                           required=True,
                           default=u'localhost')

    server_port = Int(title=_("ZEO server port"),
                      description=_("Port number of ZEO server"),
                      required=True,
                      default=8100)

    storage = TextLine(title=_("ZEO server storage"),
                       description=_("Storage name on ZEO server"),
                       required=True,
                       default=u'1')

    username = TextLine(title=_("ZEO user name"),
                        description=_("User name on ZEO server"),
                        required=False)

    password = Password(title=_("ZEO password"),
                        description=_("User password on ZEO server"),
                        required=False)

    server_realm = TextLine(title=_("ZEO server realm"),
                            description=_("Realm name on ZEO server"),
                            required=False)

    blob_dir = TextLine(title=_("BLOBs directory"),
                        description=_("Directory path for blob data"),
                        required=False)

    shared_blob_dir = Bool(title=_("Shared BLOBs directory ?"),
                           description=_("""Flag whether the blob_dir is a server-shared filesystem """
                                         """that should be used instead of transferring blob data over zrpc."""),
                           required=True,
                           default=False)

    connection = Attribute(_("Opened ZEO connection"))

    def getSettings(self):
        """Get ZEO connection setting as a JSON dict"""

    def update(self, settings):
        """Update internal fields with given settings dict"""

    def getConnection(self, wait=False, get_storage=False):
        """Open ZEO connection with given settings"""

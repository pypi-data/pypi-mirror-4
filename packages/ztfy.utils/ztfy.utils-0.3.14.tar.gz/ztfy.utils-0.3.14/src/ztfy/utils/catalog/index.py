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
import re
from persistent import Persistent
from BTrees import IFBTree

# import Zope3 interfaces
from zope.index.interfaces import IInjection, IStatistics, IIndexSearch
from zopyx.txng3.core.interfaces import IStorageWithTermFrequency
from zopyx.txng3.core.interfaces.ting import ITingIndex

# import local interfaces

# import Zope3 packages
from zope.catalog.attribute import AttributeIndex
from zope.component import createObject
from zope.container.contained import Contained
from zope.interface import implements
from zopyx.txng3.core import config
from zopyx.txng3.core.index import Index

# import local packages
from hurry.query.query import IndexTerm


class TextIndexNG(AttributeIndex, Persistent, Contained):
    """Adaptation of zopyx.txng3.core for use zope.catalog index"""

    implements(IInjection, IStatistics, IIndexSearch, ITingIndex)

    def __init__(self,
                 field_name=None,
                 interface=None,
                 field_callable=False,
                 use_stemmer=config.defaults['use_stemmer'],
                 dedicated_storage=config.defaults['dedicated_storage'],
                 ranking=config.defaults['ranking'],
                 use_normalizer=config.defaults['use_normalizer'],
                 languages=config.DEFAULT_LANGUAGE,
                 use_stopwords=config.defaults['use_stopwords'],
                 autoexpand_limit=config.defaults['autoexpand_limit'],
                 splitter=config.DEFAULT_SPLITTER,
                 index_unknown_languages=config.defaults['index_unknown_languages'],
                 query_parser=config.DEFAULT_PARSER,
                 lexicon=config.DEFAULT_LEXICON,
                 splitter_additional_chars=config.defaults['splitter_additional_chars'],
                 storage=config.DEFAULT_STORAGE,
                 splitter_casefolding=config.defaults['splitter_casefolding']):
        spaces = re.compile(r'\s+')
        if ranking:
            util = createObject(storage)
            if not IStorageWithTermFrequency.providedBy(util):
                raise ValueError("This storage cannot be used for ranking")
        _fields = spaces.split(field_name)
        AttributeIndex.__init__(self, _fields[0], interface, field_callable)
        if len(_fields) < 2:
            dedicated_storage = False
        self._index = Index(fields=_fields,
                            languages=spaces.split(languages),
                            use_stemmer=use_stemmer,
                            dedicated_storage=dedicated_storage,
                            ranking=ranking,
                            use_normalizer=use_normalizer,
                            use_stopwords=use_stopwords,
                            storage=storage,
                            autoexpand_limit=autoexpand_limit,
                            splitter=splitter,
                            lexicon=lexicon,
                            index_unknown_languages=index_unknown_languages,
                            query_parser=query_parser,
                            splitter_additional_chars=splitter_additional_chars,
                            splitter_casefolding=splitter_casefolding)
        self.languages = languages
        self.use_stemmer = use_stemmer
        self.dedicated_storage = dedicated_storage
        self.ranking = ranking
        self.use_normalizer = use_normalizer
        self.use_stopwords = use_stopwords
        self.interface = interface
        self.storage = storage
        self.autoexpand_limit = autoexpand_limit
        self.default_field = _fields[0]
        self._fields = _fields
        self.splitter = splitter
        self.lexicon = lexicon
        self.index_unknown_languages = index_unknown_languages
        self.query_parser = query_parser
        self.splitter_additional_chars = splitter_additional_chars
        self.splitter_casefolding = splitter_casefolding

    def clear(self):
        self._index.clear()

    def documentCount(self):
        """See interface IStatistics"""
        return len(self._index.getStorage(self.default_field))

    def wordCount(self):
        """See interface IStatistics"""
        return len(self._index.getLexicon())

    def index_doc(self, docid, value):
        """See interface IInjection"""
        self.unindex_doc(docid)
        v = self.interface(value, None)
        if v is not None:
            self._index.index_object(v, docid)

    def unindex_doc(self, docid):
        """See interface IInjection"""
        self._index.unindex_object(docid)

    def apply(self, query):
        if isinstance(query, dict):
            kw = query
            query = kw['query']
            del kw['query']
        ting_rr = self._index.search(query, **kw)
        return ting_rr.getDocids().keys()


class Text(IndexTerm):
    """hurry.query search term"""

    def __init__(self, index_id, text):
        super(Text, self).__init__(index_id)
        self.text = text

    def getIndex(self, context=None):
        index = super(Text, self).getIndex(context)
        assert ITingIndex.providedBy(index)
        return index

    def apply(self, context=None):
        index = self.getIndex(context)
        return IFBTree.IFSet(index.apply(self.text))

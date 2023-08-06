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

# import Zope3 interfaces
from zope.schema.interfaces import IVocabularyFactory, IChoice

# import local interfaces

# import Zope3 packages
from zope.i18n import translate
from zope.interface import classProvides, implements
from zope.schema import Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# import local packages
from ztfy.utils.request import queryRequest

from ztfy.utils import _


ENCODINGS = {
              'ascii': _('English (ASCII)'),
              'big5': _('Traditional Chinese (big5)'),
              'big5hkscs': _('Traditional Chinese (big5hkscs)'),
              'cp037': _('English (cp037)'),
              'cp424': _('Hebrew (cp424)'),
              'cp437': _('English (cp437)'),
              'cp500': _('Western Europe (cp500)'),
              'cp720': _('Arabic (cp720)'),
              'cp737': _('Greek (cp737)'),
              'cp775': _('Baltic languages (cp775)'),
              'cp850': _('Western Europe (cp850)'),
              'cp852': _('Central and Eastern Europe (cp852)'),
              'cp855': _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian (cp855)'),
              'cp856': _('Hebrew (cp856)'),
              'cp857': _('Turkish (cp857)'),
              'cp858': _('Western Europe (cp858)'),
              'cp860': _('Portuguese (cp860)'),
              'cp861': _('Icelandic (cp861)'),
              'cp862': _('Hebrew (cp862)'),
              'cp863': _('Canadian (cp863)'),
              'cp864': _('Arabic (cp864)'),
              'cp865': _('Danish, Norwegian (cp865)'),
              'cp866': _('Russian (cp866)'),
              'cp869': _('Greek (cp869)'),
              'cp874': _('Thai (cp874)'),
              'cp875': _('Greek (cp875)'),
              'cp932': _('Japanese (cp932)'),
              'cp949': _('Korean (cp949)'),
              'cp950': _('Traditional Chinese (cp950)'),
              'cp1006': _('Urdu (cp1006)'),
              'cp1026': _('Turkish (cp1026)'),
              'cp1140': _('Western Europe (cp1140)'),
              'cp1250': _('Central and Eastern Europe (cp1250)'),
              'cp1251': _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian (cp1251)'),
              'cp1252': _('Western Europe (cp1252)'),
              'cp1253': _('Greek (cp1253)'),
              'cp1254': _('Turkish (cp1254)'),
              'cp1255': _('Hebrew (cp1255)'),
              'cp1256': _('Arabic (cp1256)'),
              'cp1257': _('Baltic languages (cp1257)'),
              'cp1258': _('Vietnamese (cp1258)'),
              'euc_jp': _('Japanese (euc_jp)'),
              'euc_jis_2004': _('Japanese (euc_jis_2004)'),
              'euc_jisx0213': _('Japanese (euc_jisx0213)'),
              'euc_kr': _('Korean (euc_kr)'),
              'gb2312': _('Simplified Chinese (gb2312)'),
              'gbk': _('Unified Chinese (gbk)'),
              'gb18030': _('Unified Chinese (gb18030)'),
              'hz': _('Simplified Chinese (hz)'),
              'iso2022_jp': _('Japanese (iso2022_jp)'),
              'iso2022_jp_1': _('Japanese (iso2022_jp_1)'),
              'iso2022_jp_2': _('Japanese, Korean, Simplified Chinese, Western Europe, Greek (iso2022_jp_2)'),
              'iso2022_jp_2004': _('Japanese (iso2022_jp_2004)'),
              'iso2022_jp_3': _('Japanese (iso2022_jp_3)'),
              'iso2022_jp_ext': _('Japanese (iso2022_jp_ext)'),
              'iso2022_kr': _('Korean (iso2022_kr)'),
              'latin_1': _('West Europe (latin_1)'),
              'iso8859_2': _('Central and Eastern Europe (iso8859_2)'),
              'iso8859_3': _('Esperanto, Maltese (iso8859_3)'),
              'iso8859_4': _('Baltic languages (iso8859_4)'),
              'iso8859_5': _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian (iso8859_5)'),
              'iso8859_6': _('Arabic (iso8859_6)'),
              'iso8859_7': _('Greek (iso8859_7)'),
              'iso8859_8': _('Hebrew (iso8859_8)'),
              'iso8859_9': _('Turkish (iso8859_9)'),
              'iso8859_10': _('Nordic languages (iso8859_10)'),
              'iso8859_13': _('Baltic languages (iso8859_13)'),
              'iso8859_14': _('Celtic languages (iso8859_14)'),
              'iso8859_15': _('Western Europe (iso8859_15)'),
              'iso8859_16': _('South-Eastern Europe (iso8859_16)'),
              'johab': _('Korean (johab)'),
              'koi8_r': _('Russian (koi8_r)'),
              'koi8_u': _('Ukrainian (koi8_u)'),
              'mac_cyrillic': _('Bulgarian, Byelorussian, Macedonian, Russian, Serbian (mac_cyrillic)'),
              'mac_greek': _('Greek (mac_greek)'),
              'mac_iceland': _('Icelandic (mac_iceland)'),
              'mac_latin2': _('Central and Eastern Europe (mac_latin2)'),
              'mac_roman': _('Western Europe (mac_roman)'),
              'mac_turkish': _('Turkish (mac_turkish)'),
              'ptcp154': _('Kazakh (ptcp154)'),
              'shift_jis': _('Japanese (shift_jis)'),
              'shift_jis_2004': _('Japanese (shift_jis_2004)'),
              'shift_jisx0213': _('Japanese (shift_jisx0213)'),
              'utf_32': _('all languages (utf_32)'),
              'utf_32_be': _('all languages (utf_32_be)'),
              'utf_32_le': _('all languages (utf_32_le)'),
              'utf_16': _('all languages (utf_16)'),
              'utf_16_be': _('all languages (BMP only - utf_16_be)'),
              'utf_16_le': _('all languages (BMP only - utf_16_le)'),
              'utf_7': _('all languages (utf_7)'),
              'utf_8': _('all languages (utf_8)'),
              'utf_8_sig': _('all languages (utf_8_sig)'),
             }


class EncodingsVocabulary(SimpleVocabulary):

    classProvides(IVocabularyFactory)

    def __init__(self, terms, *interfaces):
        request = queryRequest()
        terms = [SimpleTerm(unicode(v), title=translate(t, context=request)) for v, t in ENCODINGS.iteritems()]
        terms.sort(key=lambda x: x.title)
        super(EncodingsVocabulary, self).__init__(terms, *interfaces)


class IEncodingField(IChoice):
    """Encoding field interface"""


class EncodingField(Choice):
    """Encoding field"""

    implements(IEncodingField)

    def __init__(self, values=None, vocabulary='ZTFY encodings', source=None, **kw):
        if 'values' in kw:
            del kw['values']
        if 'source' in kw:
            del kw['source']
        kw['vocabulary'] = vocabulary
        super(EncodingField, self).__init__(**kw)

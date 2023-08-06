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
import codecs
import string

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages


_unicodeTransTable = {}
def _fillUnicodeTransTable():
    _corresp = [
        (u"A", [0x00C0, 0x00C1, 0x00C2, 0x00C3, 0x00C4, 0x00C5, 0x0100, 0x0102, 0x0104]),
        (u"AE", [0x00C6]),
        (u"a", [0x00E0, 0x00E1, 0x00E2, 0x00E3, 0x00E4, 0x00E5, 0x0101, 0x0103, 0x0105]),
        (u"ae", [0x00E6]),
        (u"C", [0x00C7, 0x0106, 0x0108, 0x010A, 0x010C]),
        (u"c", [0x00E7, 0x0107, 0x0109, 0x010B, 0x010D]),
        (u"D", [0x00D0, 0x010E, 0x0110]),
        (u"d", [0x00F0, 0x010F, 0x0111]),
        (u"E", [0x00C8, 0x00C9, 0x00CA, 0x00CB, 0x0112, 0x0114, 0x0116, 0x0118, 0x011A]),
        (u"e", [0x00E8, 0x00E9, 0x00EA, 0x00EB, 0x0113, 0x0115, 0x0117, 0x0119, 0x011B]),
        (u"G", [0x011C, 0x011E, 0x0120, 0x0122]),
        (u"g", [0x011D, 0x011F, 0x0121, 0x0123]),
        (u"H", [0x0124, 0x0126]),
        (u"h", [0x0125, 0x0127]),
        (u"I", [0x00CC, 0x00CD, 0x00CE, 0x00CF, 0x0128, 0x012A, 0x012C, 0x012E, 0x0130]),
        (u"i", [0x00EC, 0x00ED, 0x00EE, 0x00EF, 0x0129, 0x012B, 0x012D, 0x012F, 0x0131]),
        (u"IJ", [0x0132]),
        (u"ij", [0x0133]),
        (u"J", [0x0134]),
        (u"j", [0x0135]),
        (u"K", [0x0136]),
        (u"k", [0x0137, 0x0138]),
        (u"L", [0x0139, 0x013B, 0x013D, 0x013F, 0x0141]),
        (u"l", [0x013A, 0x013C, 0x013E, 0x0140, 0x0142]),
        (u"N", [0x00D1, 0x0143, 0x0145, 0x0147, 0x014A]),
        (u"n", [0x00F1, 0x0144, 0x0146, 0x0148, 0x0149, 0x014B]),
        (u"O", [0x00D2, 0x00D3, 0x00D4, 0x00D5, 0x00D6, 0x00D8, 0x014C, 0x014E, 0x0150]),
        (u"o", [0x00F2, 0x00F3, 0x00F4, 0x00F5, 0x00F6, 0x00F8, 0x014D, 0x014F, 0x0151]),
        (u"OE", [0x0152]),
        (u"oe", [0x0153]),
        (u"R", [0x0154, 0x0156, 0x0158]),
        (u"r", [0x0155, 0x0157, 0x0159]),
        (u"S", [0x015A, 0x015C, 0x015E, 0x0160]),
        (u"s", [0x015B, 0x015D, 0x015F, 0x01610, 0x017F]),
        (u"T", [0x0162, 0x0164, 0x0166]),
        (u"t", [0x0163, 0x0165, 0x0167]),
        (u"U", [0x00D9, 0x00DA, 0x00DB, 0x00DC, 0x0168, 0x016A, 0x016C, 0x016E, 0x0170, 0x172]),
        (u"u", [0x00F9, 0x00FA, 0x00FB, 0x00FC, 0x0169, 0x016B, 0x016D, 0x016F, 0x0171]),
        (u"W", [0x0174]),
        (u"w", [0x0175]),
        (u"Y", [0x00DD, 0x0176, 0x0178]),
        (u"y", [0x00FD, 0x00FF, 0x0177]),
        (u"Z", [0x0179, 0x017B, 0x017D]),
        (u"z", [0x017A, 0x017C, 0x017E])
        ]
    for char, codes in _corresp:
        for code in codes :
            _unicodeTransTable[code] = char

_fillUnicodeTransTable()


def translateString(s, escapeSlashes=False, forceLower=True, spaces=' ') :
    """Remove extended characters from string and replace them with 'basic' ones
    
    @param s: text to be cleaned.
    @type s: str or unicode
    @param escapeSlashes: if True, slashes are also converted
    @type escapeSlashes: boolean
    @param forceLower: if True, result is automatically converted to lower case
    @type forceLower: boolean
    @return: text without diacritics
    @rtype: unicode
    """
    if escapeSlashes:
        s = string.replace(s, "\\", "/").split("/")[-1]
    s = s.strip()
    if isinstance(s, str):
        s = unicode(s, "utf8", "replace")
    s = s.translate(_unicodeTransTable)
    s = ''.join([a for a in s.translate(_unicodeTransTable) if a.replace(' ', '-') in (string.ascii_letters + string.digits + '_-.')])
    if forceLower:
        s = s.lower()
    if spaces != ' ':
        s = s.replace(' ', spaces)
    return s


def nvl(value, default=''):
    """Get specified value, or an empty string if value is empty
    
    @param value: text to be checked
    @param default: default value
    @return: value, or default if value is empty
    """
    return value or default


def uninvl(value, default=u''):
    """Get specified value converted to unicode, or an empty unicode string if value is empty
    
    @param value: text to be checked
    @type value: str or unicode
    @param default: default value
    @return: value, or default if value is empty
    @rtype: unicode
    """
    try:
        if isinstance(value, unicode):
            return value
        return codecs.decode(value or default)
    except:
        return codecs.decode(value or default, 'latin1')


def unidict(value):
    """Get specified dict with values converted to unicode
    
    @param value: input dict of strings which may be converted to unicode
    @type value: dict
    @return: input dict converted to unicode
    @rtype: dict
    """
    result = {}
    for key in value:
        result[key] = uninvl(value[key])
    return result


def unilist(value):
    """Get specified list with values converted to unicode
    
    @param value: input list of strings which may be converted to unicode
    @type value: list
    @return: input list converted to unicode
    @rtype: list
    """
    if not isinstance(value, (list, tuple)):
        return uninvl(value)
    return [uninvl(v) for v in value]


def utf8(value):
    """Convert given value to UTF-8"""
    if isinstance(value, unicode):
        value = value.encode('utf8')
    return value

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
from sgmllib import SGMLParser

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages


class HTMLParser(SGMLParser):

    data = ''
    entitydefs = { 'amp': '&', 'lt': '<', 'gt': '>',
                   'apos': "'", 'quot': '"',
                   'Agrave': 'À', 'Aacute': 'A', 'Acirc': 'Â', 'Atilde': 'A', 'Auml': 'Ä', 'Aring': 'A',
                   'AElig': 'AE',
                   'Ccedil': 'Ç',
                   'Egrave': 'É', 'Eacute': 'È', 'Ecirc': 'Ê', 'Euml': 'Ë',
                   'Igrave': 'I', 'Iacute': 'I', 'Icirc': 'I', 'Iuml': 'I',
                   'Ntilde': 'N',
                   'Ograve': 'O', 'Oacute': 'O', 'Ocirc': 'Ô', 'Otilde': 'O', 'Ouml': 'Ö', 'Oslash': 'O',
                   'Ugrave': 'Ù', 'Uacute': 'U', 'Ucirc': 'Û', 'Uuml': 'Ü',
                   'Yacute': 'Y',
                   'THORN': 'T',
                   'agrave': 'à', 'aacute': 'a', 'acirc': 'â', 'atilde': 'a', 'auml': 'ä', 'aring': 'a', 'aelig': 'ae',
                   'ccedil': 'ç',
                   'egrave': 'è', 'eacute': 'é', 'ecirc': 'ê', 'euml': 'ë',
                   'igrave': 'i', 'iacute': 'i', 'icirc': 'î', 'iuml': 'ï',
                   'ntilde': 'n',
                   'ograve': 'o', 'oacute': 'o', 'ocirc': 'ô', 'otilde': 'o', 'ouml': 'ö', 'oslash': 'o',
                   'ugrave': 'ù', 'uacute': 'u', 'ucirc': 'û', 'uuml': 'ü',
                   'yacute': 'y',
                   'thorn': 't',
                   'yuml': 'ÿ' }

    charrefs = {  34 : '"', 38 : '&', 39 : "'",
                  60 : '<', 62 : '>',
                 192 : 'À', 193 : 'A', 194 : 'Â', 195 : 'A', 196 : 'Ä', 197 : 'A',
                 198 : 'AE',
                 199 : 'Ç',
                 200 : 'È', 201 : 'É', 202 : 'Ê', 203 : 'Ë',
                 204 : 'I', 205 : 'I', 206 : 'Î', 207 : 'Ï',
                 208 : 'D',
                 209 : 'N',
                 210 : 'O', 211 : 'O', 212 : 'Ô', 213 : 'O', 214 : 'Ö', 216 : 'O',
                 215 : 'x',
                 217 : 'Ù', 218 : 'U', 219 : 'Û', 220 : 'Ü',
                 221 : 'Y', 222 : 'T',
                 223 : 'sz',
                 224 : 'à', 225 : 'a', 226 : 'â', 227 : 'a', 228 : 'ä', 229 : 'a',
                 230 : 'ae',
                 231 : 'ç',
                 232 : 'è', 233 : 'é', 234 : 'ê', 235 : 'ë',
                 236 : 'i', 237 : 'i', 238 : 'î', 239 : 'ï',
                 240 : 'e',
                 241 : 'n',
                 242 : 'o', 243 : 'o', 244 : 'ô', 245 : 'o', 246 : 'ö', 248 : 'o',
                 249 : 'ù', 250 : 'u', 251 : 'û', 252 : 'ü',
                 253 : 'y', 255 : 'ÿ' }

    def handle_data(self, data):
        try:
            self.data += data
        except:
            self.data += unicode(data, 'utf8')

    def handle_charref(self, name):
        try:
            n = int(name)
        except ValueError:
            self.unknown_charref(name)
            return
        if not 0 <= n <= 255:
            self.unknown_charref(name)
            return
        self.handle_data(self.charrefs.get(n) or unicode(chr(n), 'latin1'))

    def start_td(self, attributes):
        self.data += ' '

    def start_p(self, attributes):
        pass

    def end_p(self):
        self.data += '\n'


def htmlToText(value):
    """Utility function to extract text content from HTML"""
    if value is None:
        return ''
    parser = HTMLParser()
    parser.feed(value)
    parser.close()
    return parser.data

### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# Python 2.6/2.7 compatibility code copied from EULExistDB
# (https://github.com/emory-libraries/eulexistdb)
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
import base64
import cookielib
import httplib
import socket
import urllib2
import xmlrpclib

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages


class TimeoutHTTP(httplib.HTTP):
    def __init__(self, host='', port=None, strict=None, timeout=None):
        if port == 0:
            port = None
        self._setup(self._connection_class(host, port, strict, timeout))

class TimeoutHTTPS(httplib.HTTPS):
    def __init__(self, host='', port=None, strict=None, timeout=None):
        if port == 0:
            port = None
        self._setup(self._connection_class(host, port, strict, timeout))


class XMLRPCCookieAuthTransport(xmlrpclib.Transport):
    """An XML-RPC transport handling authentication via cookies"""

    _http_connection = httplib.HTTPConnection
    _http_connection_compat = TimeoutHTTP

    def __init__(self, user_agent, credentials=(), cookies=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        xmlrpclib.Transport.__init__(self)
        self.user_agent = user_agent
        self.credentials = credentials
        self.cookies = cookies
        self.timeout = timeout
        if self._connection_required_compat():
            self.make_connection = self._make_connection_compat
            self.get_response = self._get_response_compat

    def _connection_required_compat(self):
        # Compatibility code copied from EULExistDB (https://github.com/emory-libraries/eulexistdb)
        # UGLY HACK ALERT. Python 2.7 xmlrpclib caches connection objects in
        # self._connection (and sets self._connection in __init__). Python
        # 2.6 and earlier has no such cache. Thus, if self._connection
        # exists, we're running the newer-style, and if it doesn't then
        # we're running older-style and thus need compatibility mode.
        try:
            self._connection
            return False
        except AttributeError:
            return True

    def make_connection(self, host):
        # This is the make_connection that runs under Python 2.7 and newer.
        # The code is pulled straight from 2.7 xmlrpclib, except replacing
        # HTTPConnection with self._http_connection
        if self._connection and host == self._connection[0]:
            return self._connection[1]
        chost, self._extra_headers, _x509 = self.get_host_info(host)
        self._connection = host, self._http_connection(chost, timeout=self.timeout)
        return self._connection[1]

    def _make_connection_compat(self, host):
        # This method runs as make_connection under Python 2.6 and older.
        # __init__ detects which version we need and pastes this method
        # directly into self.make_connection if necessary.
        host, _extra_headers, _x509 = self.get_host_info(host)
        return self._http_connection_compat(host, timeout=self.timeout)

    # override the send_host hook to also send authentication info
    def send_host(self, connection, host):
        xmlrpclib.Transport.send_host(self, connection, host)
        if (self.cookies is not None) and (len(self.cookies) > 0):
            for cookie in self.cookies:
                connection.putheader('Cookie', '%s=%s' % (cookie.name, cookie.value))
        elif self.credentials:
            auth = 'Basic %s' % base64.encodestring("%s:%s" % self.credentials).strip()
            connection.putheader('Authorization', auth)

    # dummy request class for extracting cookies
    class CookieRequest(urllib2.Request):
        pass

    # dummy response info headers helper
    class CookieResponseHelper:
        def __init__(self, response):
            self.response = response
        def getheaders(self, header):
            return self.response.msg.getallmatchingheaders(header)

    # dummy response class for extracting cookies
    class CookieResponse:
        def __init__(self, response):
            self.response = response
        def info(self):
            return XMLRPCCookieAuthTransport.CookieResponseHelper(self.response)

    # dummy compat response class for extracting cookies
    class CompatCookieResponse:
        def __init__(self, headers):
            self.headers = headers
        def info(self):
            return self.headers

    def request(self, host, handler, request_body, verbose=False):
        # issue XML-RPC request
        connection = self.make_connection(host)
        self.verbose = verbose
        if verbose:
            connection.set_debuglevel(1)
        self.send_request(connection, handler, request_body)
        self.send_host(connection, host)
        self.send_user_agent(connection)
        self.send_content(connection, request_body)
        # get response
        return self.get_response(connection, host, handler)

    def get_response(self, connection, host, handler):
        response = connection.getresponse()
        # extract cookies from response headers
        if self.cookies is not None:
            crequest = XMLRPCCookieAuthTransport.CookieRequest('http://%s/' % host)
            cresponse = XMLRPCCookieAuthTransport.CookieResponse(response)
            self.cookies.extract_cookies(cresponse, crequest)
        if response.status != 200:
            raise xmlrpclib.ProtocolError(host + handler, response.status, response.reason, response.getheaders())
        return self.parse_response(response)

    def _get_response_compat(self, connection, host, handler):
        errcode, errmsg, headers = connection.getreply()
        # extract cookies from response headers
        if self.cookies is not None:
            crequest = XMLRPCCookieAuthTransport.CookieRequest('http://%s/' % host)
            cresponse = XMLRPCCookieAuthTransport.CompatCookieResponse(headers)
            self.cookies.extract_cookies(cresponse, crequest)
        if errcode != 200:
            raise xmlrpclib.ProtocolError(host + handler, errcode, errmsg, headers)
        try:
            sock = connection._conn.sock
        except AttributeError:
            sock = None
        return self._parse_response(connection.getfile(), sock)


class SecureXMLRPCCookieAuthTransport(XMLRPCCookieAuthTransport):
    """Secure XML-RPC transport"""

    _http_connection = httplib.HTTPSConnection
    _http_connection_compat = TimeoutHTTPS


def getClient(uri, credentials=(), verbose=False, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
    """Get an XML-RPC client which supports basic authentication"""
    if uri.startswith('https:'):
        transport = SecureXMLRPCCookieAuthTransport('Python XML-RPC Client/0.1 (ZTFY secure transport)', credentials, timeout=timeout)
    else:
        transport = XMLRPCCookieAuthTransport('Python XML-RPC Client/0.1 (ZTFY basic transport)', credentials, timeout=timeout)
    return xmlrpclib.Server(uri, transport=transport, verbose=verbose)


def getClientWithCookies(uri, credentials=(), verbose=False, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
    """Get an XML-RPC client which supports authentication throught cookies"""
    if uri.startswith('https:'):
        transport = SecureXMLRPCCookieAuthTransport('Python XML-RPC Client/0.1 (ZTFY secure cookie transport)', credentials, cookielib.CookieJar(), timeout)
    else:
        transport = XMLRPCCookieAuthTransport('Python XML-RPC Client/0.1 (ZTFY secure cookie transport)', credentials, cookielib.CookieJar(), timeout)
    return xmlrpclib.Server(uri, transport=transport, verbose=verbose)

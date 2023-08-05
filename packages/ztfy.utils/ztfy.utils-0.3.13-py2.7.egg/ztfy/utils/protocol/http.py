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
import httplib2
import urllib

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages


class HTTPClient(object):
    """HTTP client"""

    def __init__(self, method, protocol, servername, url, params={}, credentials=(),
                 proxy=(), rdns=True, proxy_auth=(), timeout=None, headers={}):
        """Intialize HTTP connection"""
        self.connection = None
        self.method = method
        self.protocol = protocol
        self.servername = servername
        self.url = url
        self.params = params
        self.location = None
        self.credentials = credentials
        self.proxy = proxy
        self.rdns = rdns
        self.proxy_auth = proxy_auth
        self.timeout = timeout
        self.headers = headers
        if 'User-Agent' not in headers:
            self.headers['User-Agent'] = 'ZTFY HTTP Client/1.0'

    def getResponse(self):
        """Common HTTP request"""
        if self.proxy:
            proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_HTTP,
                                            proxy_host=self.proxy[0],
                                            proxy_port=self.proxy[1],
                                            proxy_rdns=self.rdns,
                                            proxy_user=self.proxy_auth and self.proxy_auth[0] or None,
                                            proxy_pass=self.proxy_auth and self.proxy_auth[1] or None)
        else:
            proxy_info = None
        http = httplib2.Http(timeout=self.timeout, proxy_info=proxy_info)
        if self.credentials:
            http.add_credentials(self.credentials[0], self.credentials[1])
        uri = '%s://%s%s' % (self.protocol, self.servername, self.url)
        if self.params:
            uri += '?' + urllib.urlencode(self.params)
        response, content = http.request(uri, self.method, headers=self.headers)
        return response, content


def getClient(method, protocol, servername, url, params={}, credentials=(), proxy=(), rdns=True, proxy_auth=(), timeout=None, headers={}):
    """HTTP client factory"""
    return HTTPClient(method, protocol, servername, url, params, credentials, proxy, rdns, proxy_auth, timeout, headers)

###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""PYPI proxy
$Id:$
"""
__docformat__ = "reStructuredText"

import os
import urllib2
import xmlrpclib
import urlparse
from ConfigParser import ConfigParser

# exposed for testing
_xmlRPCServerProxyClass = xmlrpclib.ServerProxy

def getPYPIRCAuth(pypiURL):
    """Returns the relevant username and password for a given pypiURL."""

    rc = os.path.join(os.path.expanduser('~'), '.pypirc')
    if os.path.exists(rc):
        realm = 'pypi'
        username = None
        password = None

        config = ConfigParser()
        config.read(rc)
        sections = config.sections()
        if 'distutils' in sections:
            # let's get the list of servers
            index_servers = config.get('distutils', 'index-servers')
            _servers = [server.strip() for server in index_servers.split('\n')
                        if server.strip() != '']
            for server in _servers:
                repos = config.get(server, 'repository')
                if pypiURL.startswith(server) or pypiURL.startswith(repos):
                    un = config.get(server, 'username')
                    pw = config.get(server, 'password')
                    if un and pw:
                        username= un
                        password = pw
                        if config.has_option(server, 'realm'):
                            realm = config.get(server, 'realm')
                        break

        if not username and not password and 'server-login' in sections:
            # old format
            server = 'server-login'
            username  = config.get(server, 'username')
            password = config.get(server, 'password')

    return realm, username, password


def urlOpener(pypiURL):
    """Open url including auth"""
    realm, username, password = getPYPIRCAuth(pypiURL)
    if username is not None and password is not None:
        hpm = urllib2.HTTPPasswordMgr()
        hpm.add_password(realm, pypiURL, username, password)
        auth = urllib2.HTTPBasicAuthHandler(hpm)
        opener = urllib2.build_opener(auth)
    else:
        opener = urllib2.build_opener()

    request = urllib2.Request(pypiURL)
    return opener.open(request)


def applyPYIRCAuthentication(pypiURL):
    """Apply username and password from .pypirc file to url."""
    realm, username, password = getPYPIRCAuth(pypiURL)
    if username and password:
        scheme, netloc, path, params, query, frag = urlparse.urlparse(pypiURL)
        host = '%s:%s@%s' % (username, password, netloc)
        pypiURL = urlparse.urlunparse((scheme, host, path, params, query, frag))

    return pypiURL


def getPYPIProxy(pypiURL):
    """Returns a pypi XML-RPC connection.
    
    Use username and password as a protocol prefix like:
    
    http://username:password@pypi.python.org/pypi
    
    """
    authURL = applyPYIRCAuthentication(pypiURL)
    if not authURL.endswith('/'):
        # use / and prevent using /RPC2 as handler
        authURL += '/'
    return _xmlRPCServerProxyClass(authURL)


def fetchPackageReleaseURLs(pypiURL, pkgName, version):
    """Fetch package releases urls.

    Note, this method dows not fetch release urls from external pages. This 
    means your spider pacakge must be located at the given pypi server. But
    this should not be a problem since we explicit offer a mypypi mirror.

    """
    res = []
    pypiProxy = getPYPIProxy(pypiURL)
    localURLs = pypiProxy.release_urls(pkgName, version)
    for data in localURLs:
        res.append({'url': data['url'],
                    'filename': data['filename'],
                    'md5_digest': data['md5_digest']})
    return res

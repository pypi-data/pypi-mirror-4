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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import base64
import copy
import logging
import os.path
import re
import rfc822
import pprint
import doctest
import urllib2
from Cookie import SimpleCookie
import StringIO
from StringIO import StringIO

import transaction

import zope.interface
import zope.component
from zope.component import hooks
from zope.publisher.interfaces import ISkinnable
from zope.publisher.skinnable import setDefaultSkin

import zope.app.appsetup.product
from zope.app.publication.httpfactory import chooseClasses

from z3c.json.proxy import JSONRPCProxy
from z3c.json.transport import BasicAuthTransport
from z3c.jsonrpc.publisher import JSON_RPC_VERSION
from z3c.json.exceptions import ProtocolError
from z3c.json.exceptions import ResponseError

import m01.stub.testing
import s01.core.mongo
import s01.worker.interfaces
import s01.worker.package
import s01.worker.publisher
import s01.worker.publish
import s01.worker.testing.debug


def getRootFolder():
    return zope.component.getUtility(s01.worker.interfaces.IScrapyRoot)


###############################################################################
#
# test helper methods
#
###############################################################################

class RENormalizer(object):
    """Normalizer which can convert text based on regex patterns"""

    def __init__(self, patterns):
        self.patterns = patterns
        self.transformers = map(self._cook, patterns)

    def _cook(self, pattern):
        if callable(pattern):
            return pattern
        regexp, replacement = pattern
        return lambda text: regexp.sub(replacement, text)

    def addPattern(self, pattern):
        patterns = list(self.patterns)
        patterns.append(pattern)
        self.transformers = map(self._cook, patterns)
        self.patterns = patterns

    def __call__(self, data):
        """Normalize a dict or text"""
        if not isinstance(data, basestring):
            data = pprint.pformat(data)
        for normalizer in self.transformers:
            data = normalizer(data)
        return data

    def pprint(self, data):
        """Pretty print data"""
        print self(str(data))


# see testing.txt for a sample usage
reNormalizer = RENormalizer([
   (re.compile("\\\\"), "/"),
   (re.compile("//"), "/"),
   (re.compile("unpack move: [a-zA-Z0-9.\\/:']+"), "unpack move: ..."),
   (re.compile("unpack: [a-zA-Z0-9.\\/:']+"), "unpack: ..."),
   (re.compile("bootstrap: Creating directory [a-zA-Z0-9.\\/:']+"),
               "bootstrap: Creating directory ..."),
   (re.compile("Creating directory [a-zA-Z0-9.\\/:']+"),
               "Creating directory ..."),
   (re.compile("s01.worker: Writing file [a-zA-Z0-9.\\/:']+"),
               "s01.worker: Writing file ..."),
   (re.compile("s01.worker: Creating directory [a-zA-Z0-9.\\/:']+"),
               "s01.worker: Creating directory ..."),
   (re.compile("s01.worker: Load settings from path [a-zA-Z0-9.\\/:']+"),
               "s01.worker: Load settings from path ..."),
   (re.compile("buildout: Develop: [a-zA-Z0-9.\\/:']+"),
               "buildout: Develop: ..."),
   (re.compile("s01.worker: Change mode [0-9]+ for [a-zA-Z0-9.\\/:']+"),
               "s01.worker: Change mode ... for ..."),
   (re.compile("list: [a-zA-Z0-9.\\/:']+"), "list: ..."),
   (re.compile("Generated script [a-zA-Z0-9.\\/:']+"), "Generated script ..."),
   (re.compile("s01.worker: Load settings given from section target [a-zA-Z0-9.\\/:']+"),
               "s01.worker: Load settings given from section target ..."),
   ])


###############################################################################
#
# test components
#
###############################################################################

headerre = re.compile(r'(\S+): (.+)$')
def split_header(header):
    return headerre.match(header).group(1, 2)

basicre = re.compile('Basic (.+)?:(.+)?$')
def auth_header(header):
    match = basicre.match(header)
    if match:
        u, p = match.group(1, 2)
        if u is None:
            u = ''
        if p is None:
            p = ''
        auth = base64.encodestring('%s:%s' % (u, p))
        return 'Basic %s' % auth[:-1]
    return header


class CookieHandler(object):

    def __init__(self, *args, **kw):
        # Somewhere to store cookies between consecutive requests
        self.cookies = SimpleCookie()
        super(CookieHandler, self).__init__(*args, **kw)

    def httpCookie(self, path):
         """Return self.cookies as an HTTP_COOKIE environment value."""
         l = [m.OutputString().split(';')[0] for m in self.cookies.values()
              if path.startswith(m['path'])]
         return '; '.join(l)

    def loadCookies(self, envstring):
        self.cookies.load(envstring)

    def saveCookies(self, response):
        """Save cookies from the response."""
        for k,v in response._cookies.items():
            k = k.encode('utf8')
            self.cookies[k] = v['value'].encode('utf8')
            if v.has_key('path'):
                self.cookies[k]['path'] = v['path']


class ScrapyTestRequest(s01.worker.publisher.ScrapyRequest):
    """ScrapyTestRequest"""

    def __init__(self, body_instream=None, environ=None, form=None,
                 skin=None, **kw):

        _testEnv =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }

        if environ is not None:
            _testEnv.update(environ)

        if kw:
            _testEnv.update(kw)
        if body_instream is None:
            from StringIO import StringIO
            body_instream = StringIO('')

        super(FasterTestRequest, self).__init__(body_instream, _testEnv)
        if form:
            self.form.update(form)

        if skin is not None:
            zope.interface.directlyProvides(self, skin)


class ResponseWrapper(object):
    """A wrapper that adds several introspective methods to a response."""

    def __init__(self, response, path, omit=()):
        self._response = response
        self._path = path
        self.omit = omit
        self._body = None

    def getOutput(self):
        """Returns the full HTTP output (headers + body)"""
        body = self.getBody()
        omit = self.omit
        headers = [x
                   for x in self._response.getHeaders()
                   if x[0].lower() not in omit]
        headers.sort()
        headers = '\n'.join([("%s: %s" % (n, v)) for (n, v) in headers])
        statusline = '%s %s' % (self._response._request['SERVER_PROTOCOL'],
                                self._response.getStatusString())
        if body:
            return '%s\n%s\n\n%s' %(statusline, headers, body)
        else:
            return '%s\n%s\n' % (statusline, headers)

    def getBody(self):
        """Returns the response body"""
        if self._body is None:
            self._body = ''.join(self._response.consumeBody())

        return self._body

    def getPath(self):
        """Returns the path of the request"""
        return self._path

    def __getattr__(self, attr):
        return getattr(self._response, attr)

    __str__ = getOutput


class HTTPCaller(CookieHandler):
    """Execute an HTTP request string via the publisher"""

    def __call__(self, request_string, handle_errors=True, form=None):
        # Commit work done by previous python code.
        transaction.commit()

        # Discard leading white space to make call layout simpler
        request_string = request_string.lstrip()

        # split off and parse the command line
        l = request_string.find('\n')
        command_line = request_string[:l].rstrip()
        request_string = request_string[l + 1:]
        method, path, protocol = command_line.split()

        instream = StringIO(request_string)
        environment = {"HTTP_COOKIE": self.httpCookie(path),
                       "HTTP_HOST": 'localhost',
                       "REQUEST_METHOD": method,
                       "SERVER_PROTOCOL": protocol,
                       }

        headers = [split_header(header)
                   for header in rfc822.Message(instream).headers]
        for name, value in headers:
            name = ('_'.join(name.upper().split('-')))
            if name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                name = 'HTTP_' + name
            environment[name] = value.rstrip()

        auth_key = 'HTTP_AUTHORIZATION'
        if environment.has_key(auth_key):
            environment[auth_key] = auth_header(environment[auth_key])

        old_site = hooks.getSite()
        hooks.setSite(None)

        request_cls, publication_cls = self.chooseRequestClass(method, path,
                                                               environment)
        debugger = FunctionalTestSetup().getDebugger()
        request = debugger._request(
            path, instream,
            environment=environment,
            request=request_cls, publication=publication_cls)
        if ISkinnable.providedBy(request):
            # only ISkinnable requests have skins
            setDefaultSkin(request)

        if form is not None:
            if request.form:
                raise ValueError("only one set of form values can be provided")
            request.form = form

        request = s01.worker.publish.publish(request,
            handle_errors=handle_errors)

        response = ResponseWrapper(
            request.response, path,
            omit=('x-content-type-warning', 'x-powered-by'),
            )

        self.saveCookies(response)
        hooks.setSite(old_site)

        return response

    def chooseRequestClass(self, method, path, environment):
        """Choose and return a request class and a publication class"""
        request_cls, publication_cls = chooseClasses(method, environment)
        
        content_type = environment.get('CONTENT_TYPE', '')
        is_json = content_type.startswith('application/json')
    
        if method in ('GET', 'POST', 'HEAD'):
            if (method == 'POST' and is_json):
                request_cls = s01.worker.publisher.ScrapyRequest
                publication_cls = s01.worker.publisher.ScrapyPublication
    
        return request_cls, publication_cls


class FunctionalTestSetup(object):
    """Keeps shared state across several functional test cases."""

    __shared_state = { '_init': False }

    def __init__(self, config_file=None, product_config=None):
        """Initializes Zope 3 framework andarses Zope3 configuration files."""
        self.__dict__ = self.__shared_state

        if not self._init:

            if not config_file:
                config_file = 'ftesting.zcml'
            self.log = StringIO()
            # Make it silent but keep the log available for debugging
            logging.root.addHandler(logging.StreamHandler(self.log))

            self.old_product_config = copy.deepcopy(
                zope.app.appsetup.product.saveConfiguration())
            configs = []
            if product_config:
                configs = zope.app.appsetup.product.loadConfiguration(
                    StringIO(product_config))
                configs = [
                    zope.app.appsetup.product.FauxConfiguration(name, values)
                    for name, values in configs.items()
                    ]
            self.local_product_config = configs
            zope.app.appsetup.product.setProductConfigurations(configs)

            # This handles anything added by generations or other bootstrap
            # subscribers.
            transaction.commit()
            self.debugger = s01.worker.testing.debug.Debugger(config_file)

            self._config_file = config_file
            self._product_config = product_config
            self._init = True

        elif config_file and config_file != self._config_file:
            # Running different tests with different configurations is not
            # supported at the moment
            raise NotImplementedError('Already configured'
                                      ' with a different config file')

        elif product_config and product_config != self._product_config:
            raise NotImplementedError('Already configured'
                                      ' with different product configuration')

    def setUp(self):
        """Prepares for a functional test case."""
        # Tear down the old demo storages (if any) and create fresh ones
        transaction.abort()
        zope.app.appsetup.product.setProductConfigurations(
            self.local_product_config)

    def tearDown(self):
        """Cleans up after a functional test case."""
        transaction.abort()
        hooks.setSite(None)

    def tearDownCompletely(self):
        """Cleans up the setup done by the constructor."""
        transaction.abort()
        zope.app.appsetup.product.restoreConfiguration(
            self.old_product_config)
        self._config_file = False
        self._product_config = None
        self._init = False

    def getRootFolder(self):
        """Returns the Zope root folder."""
        return getRootFolder()

    def getDebugger(self):
        """Returns the Zope application instance."""
        return self.debugger


class ZCMLLayer:
    """ZCML-defined test layer
    """

    __bases__ = ()

    def __init__(self, config_file, module, name, allow_teardown=False,
                 product_config=None):
        self.config_file = config_file
        self.__module__ = module
        self.__name__ = name
        self.allow_teardown = allow_teardown
        self.product_config = product_config

    def setUp(self):
        self.setup = FunctionalTestSetup(
            self.config_file, product_config=self.product_config)

    def tearDown(self):
        self.setup.tearDownCompletely()
        if not self.allow_teardown:
            # Some ZCML directives change globals but are not accompanied
            # with registered CleanUp handlers to undo the changes.  Let
            # packages which use such directives indicate that they do not
            # support tearing down.
            raise NotImplementedError


def prepareDocTestKeywords(kw):
    globs = kw.setdefault('globs', {})
    if globs.get('getRootFolder') is None:
        globs['getRootFolder'] = getRootFolder

    kwsetUp = kw.get('setUp')
    def setUp(test):
        test.globs['http'] = HTTPCaller()
        FunctionalTestSetup().setUp()
        if kwsetUp is not None:
            kwsetUp(test)
    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        if kwtearDown is not None:
            kwtearDown(test)
        FunctionalTestSetup().tearDown()
    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old
                             | doctest.ELLIPSIS
                             | doctest.NORMALIZE_WHITESPACE)


###############################################################################
#
# Test proxy
#
###############################################################################

class JSONRPCTestTransport(BasicAuthTransport):
    """Test transport that delegates to zope.app.testing.functional.HTTPCaller.

    It can be used like a normal transport, including support for basic 
    authentication.
    """

    verbose = False
    handleErrors = True

    def request(self, host, handler, request_body, verbose=0):
        request = "POST %s HTTP/1.0\n" % (handler,)
        request += "Content-Length: %i\n" % len(request_body)
        request += "Content-Type: application/json\n"

        host, extra_headers, x509 = self.get_host_info(host)
        if extra_headers:
            request += "Authorization: %s\n" % (
                dict(extra_headers)["Authorization"],)

        elif self.username and self.password:
            up = "%s:%s" % (self.username, self.password)
            up = base64.encodestring(up).replace("\012", "")
            request += "AUTHORIZATION: Basic %s\n" % up

        request += "\n" + request_body
        caller = HTTPCaller()
        response = caller(request, handle_errors=self.handleErrors)

        errcode = response.getStatus()
        errmsg = response.getStatusString()
        # This is not the same way that the normal transport deals with the
        # headers.
        headers = response.getHeaders()

        if errcode != 200:
            raise ProtocolError(host + handler, errcode, errmsg, headers)

        return self._parse_response(StringIO(response.getBody()), sock=None)


def ScrapyTestProxy(uri, username, password, transport=None, encoding=None, 
    verbose=None, jsonId=None, handleErrors=True, jsonVersion=JSON_RPC_VERSION):
    """A factory that creates a server proxy using the ZopeJSONRPCTestTransport 
    by default."""
    if verbose is None:
        verbose = 0
    if transport is None:
        transport = JSONRPCTestTransport(username, password)
    if isinstance(transport, JSONRPCTestTransport):
        transport.handleErrors = handleErrors
    return JSONRPCProxy(uri, transport, encoding, verbose, jsonId, jsonVersion)


###############################################################################
#
# Fake pypi server
#
###############################################################################



S01_DEMO_VERSIONS = ['0.16.2']

PACKAGES = {
    's01.demo': S01_DEMO_VERSIONS,
}

PKGS = {}
    

class FakeXMLServerProxy(object):
    """Fake XMLRPC PYPI server API."""

    def __init__(self, url, transport=None, allow_none=0):
        self.url = url
        self.transport = transport

    def list_packages(self):
        """Retrieve a list of the package names registered with the package
        index.

        Returns a list of name strings.
        """
        return list(PACKAGES.keys())

    def package_releases(self, packageName, show_hidden=False):
        """Retrieve a list of the releases registered for the given package
        name.

        Returns a list of version strings.
        """
        try:
            package = PACKAGES[packageName]

            if show_hidden:
                return package
            else:
                return [package[0]]
        except KeyError:
            return []

    def release_urls(self, packageName, version):
        if packageName == 's01.demo':
            if version == '0.16.2':
                return [
                    {'has_sig': False,
                     'comment_text': '',
                     'python_version': 'source',
                     'url': 'http://pypi.python.org/packages/source/s01.demo/s01.demo-0.16.2.zip',
                     'md5_digest': 'bd915cb15f2b1929490321e6eb70daca',
                     'downloads': 153,
                     'filename': 's01.demo-0.16.2.zip',
                     'packagetype': 'sdist',
                     'size': 25682}]

        raise KeyError("Testdata not supported for '%s' version '%s'" % (
            packageName, version))

    def release_data(self, packageName, version):
        if packageName == 's01.demo':
            if version == '0.16.2':
                return {
                    'maintainer': None,
                    'maintainer_email': None,
                    'cheesecake_code_kwalitee_id': None,
                    'keywords': 'zope3 form widget',
                    'author': 'Stephan Richter, Roger Ineichen and the Zope Community <zope-dev at zope org>',
                    'author_email': 'zope3-dev@zope.org',
                    'download_url': 'UNKNOWN',
                    'platform': 'UNKNOWN',
                    'version': version,
                    'obsoletes': [],
                    'provides': [],
                    'cheesecake_documentation_id': None,
                    '_pypi_hidden': 1,
                    'description': "This package provides an --- Release",
                    '_pypi_ordering': 10,
                    'classifiers': ['Development Status :: 5 - Production/Stable',
                        'Environment :: Web Environment',
                        'Framework :: Zope3',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: Zope Public License',
                        'Natural Language :: English',
                        'Operating System :: OS Independent',
                        'Programming Language :: Python',
                        'Topic :: Internet :: WWW/HTTP'],
                    'name': 'z3c.form',
                    'license': 'ZPL 2.1',
                    'summary': 'IAuthentication implementation for for Zope3',
                    'home_page': 'http://pypi.python.org/pypi/s01.demo',
                    'stable_version': None,
                    'requires': [],
                    'cheesecake_installability_id': None}


        raise KeyError("Testdata not supported for '%s' version '%s'" % (
            packageName, version))

    def __repr__(self):
        return "<%s for %r>" %(self.__class__.__name__, self.url)


class FakeURLOpener(object):
    """FAke url opener which can return the package data"""

    def __init__(self, url):
        self.url = url

    def read(self, mode=None):
        # returns the package data
        try:
            fPath = PKGS[self.url]
            f = open(fPath, 'rb')
            data = f.read()
            f.close()
            return data
        except KeyError:
            raise urllib2.HTTPError(self.url, 404, 'Not found', {}, None)


_orgXMLRPCServerProxyClass = None
_orgUrlOpener = None

def setUpPackages():
    global PKGS
    pkgDir = os.path.join(os.path.dirname(__file__), 'pypi')
    for fName in os.listdir(pkgDir):
        if fName.startswith('.svn'):
            continue
        pkgName = fName.split('-')[0]
        url = 'http://pypi.python.org/packages/source/%s/%s' % (pkgName, fName)
        fPath = os.path.join(pkgDir, fName)
        PKGS[url] = fPath
    # remove previous installed spider packages
    topDir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
    pkgDir = os.path.join(topDir, 'parts', 'test-pkgs')
    if os.path.exists(pkgDir):
        for fName in os.listdir(pkgDir):
            p = os.path.join(pkgDir, fName)
            s01.worker.package.rmtree(p)

def tearDownPackages():
    global PKGS
    PKGS = {}

def setUpFakePYPI(test=None):
    # setup PGKS
    setUpPackages()
    # setup fake pypi
    global _orgXMLRPCServerProxyClass
    _orgXMLRPCServerProxyClass = s01.worker.pypi._xmlRPCServerProxyClass
    s01.worker.pypi._xmlRPCServerProxyClass = FakeXMLServerProxy
    # setup fake opener
    global _orgUrlOpener
    _orgUrlOpener = s01.worker.pypi.urlOpener
    s01.worker.pypi.urlOpener = FakeURLOpener

def tearDownFakePYPI(test=None):
    # tear down PKGS
    tearDownPackages()
    # tear down fake pypi
    global _orgXMLRPCServerProxyClass
    s01.worker.pypi._xmlRPCServerProxyClass = _orgXMLRPCServerProxyClass
    _orgXMLRPCServerProxyClass = None
    # tear down fake opener
    global _orgUrlOpener
    s01.worker.pypi.urlOpener = _orgUrlOpener
    _orgUrlOpener = None


###############################################################################
#
# Testing layer
#
###############################################################################

#HERE = os.path.dirname(__file__)
#FTESTING_ZCML = os.path.join(HERE, 'ftesting.zcml')
#FTESTING_ZCML = os.path.abspath(FTESTING_ZCML)
#ScrapyZCMLLayer = ZCMLLayer(FTESTING_ZCML, __name__, 'Functional')

ScrapyZCMLLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'ScrapyZCMLLayer', allow_teardown=True)


###############################################################################
#
# setup helper
#
###############################################################################

def setUpMongoDB(test=None):
    host = 'localhost'
    port = 45017
    mongoDir = os.path.join(os.path.dirname(__file__), 'mongodb')
    sandBoxDir = os.path.join(mongoDir, 'sandbox')
    dataDir = os.path.join(mongoDir, 'data')
    m01.stub.testing.startMongoDBServer(host, port, sandBoxDir=sandBoxDir,
        dataDir=dataDir)
    # ensure that we use a new connection pool
    pool = s01.core.mongo.mongoConnectionPool
    pool.disconnect()


def tearDownMongoDB(test=None):
    m01.stub.testing.stopMongoDBServer()


###############################################################################
#
# Doctest setup
#
###############################################################################

def doctestSetUp(test):
    """Setup additional compnents everything else if done by ftesting.zcml."""
    setUpMongoDB()
    setUpFakePYPI()


def doctestTearDown(test):
    """Tear down additional components"""
    tearDownMongoDB()
    tearDownFakePYPI()


###############################################################################
#
# Doctest setup
#
###############################################################################

def ScrapyDocFileSuite(*paths, **kw):
    """Build a functional test suite from a text file."""
    globs = kw.setdefault('globs', {})
    globs['getRootFolder'] = getRootFolder
    kw['setUp'] = kw.get('setUp', doctestSetUp)
    kw['tearDown'] = kw.get('tearDown', doctestTearDown)
    kw['package'] = doctest._normalize_module(kw.get('package'))
    prepareDocTestKeywords(kw)
    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = ScrapyZCMLLayer
    return suite

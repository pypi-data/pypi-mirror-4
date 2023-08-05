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

import os.path
import zope.interface
import zope.component.interfaces
import zope.location.interfaces
import z3c.jsonrpc.interfaces
import m01.mongo.interfaces
import m01.remote.interfaces

def isDirectory(path):
    return os.path.isdir(path)

def isPath(path):
    return os.path.isfile(path)


class IWSGIApplication(zope.interface.Interface):
    """A WSGI application."""

    def __call__(environ, start_response):
        """Called by a WSGI server.

        The ``environ`` parameter is a dictionary object, containing CGI-style
        environment variables. This object must be a builtin Python dictionary
        (not a subclass, UserDict or other dictionary emulation), and the
        application is allowed to modify the dictionary in any way it
        desires. The dictionary must also include certain WSGI-required
        variables (described in a later section), and may also include
        server-specific extension variables, named according to a convention
        that will be described below.

        The ``start_response`` parameter is a callable accepting two required
        positional arguments, and one optional argument. For the sake of
        illustration, we have named these arguments ``status``,
        ``response_headers``, and ``exc_info``, but they are not required to
        have these names, and the application must invoke the
        ``start_response`` callable using positional arguments
        (e.g. ``start_response(status, response_headers)``).
        """


class IScrapyRoot(m01.mongo.interfaces.IMongoStorage,
    m01.remote.interfaces.IRemoteProcessor, zope.location.interfaces.IRoot,
    zope.component.interfaces.ISite, zope.location.interfaces.ILocation):
    """Worker which processes buildout based scrapy spider packages"""

    serverName = zope.schema.TextLine(
        title=u'Server Name',
        description=u'Server Name (unique if you use more then one server)',
        required=True)

    pkgsDir = zope.schema.TextLine(
        title=u'Scrapy Spider package installation directory path',
        description=u'Scrapy Spider package installation directory path',
        constraint=isDirectory,
        max_length=255,
        required=True)

    # we only use one pypi index server, use mypypi if you need one see:
    # http://pypi.python.org/pypi/mypypi
    pypiURL = zope.schema.URI(
        title=u'PYPI index URL',
        description=u'PYPI index URL',
        required=True)

    defaultPythonVersion = zope.schema.TextLine(
        title=u'Default Python Version',
        description=u'Default Python Version',
        required=True)

    # only used if pythonVersion argument is used in addPackage method
    pythonVersions = zope.schema.Dict(
        title=u'python-version:path mapping (optional)',
        description=u'python-version:path mapping (optional)',
        key_type=zope.schema.TextLine(
            title=u'Python Version (as string)',
            required=True),
        value_type=zope.schema.TextLine(
            title=u'Python executable path',
            constraint=isPath,
            required=True),
        default={},
        required=False)

    def getStartTime():
        """Returns the server start time"""

    def getProcessorStartTime():
        """Returns the server start time"""

    def getSchedulerStartTime():
        """Returns the server start time"""

    # ScrapyPackage management API used by package manager
    def doEnsureScrapyPackage(pkgName, pkgVersion, pyVersion, md5Digest,
        spiderNames):
        """Ensures that a package and version is stored in the mongodb."""

    def doRemoveScrapyPackage(pkgName, pkgVersion, pyVersion):
        """Remove an existing ScrapyPackage"""

    # buildout package management API
    def queryPackage(pkgName, pkgVersion):
        """Returns a package for given pkgName and pkgVersion or None"""

    def hasPackage(pkgName, version):
        """Retruns True or False if a package version is given"""

    def getMissingPackageVersions(serverName):
        """Returns a list of missing packages/version data compared to another
        server by it's serverName.
        """

    def addPackage(pkgName, pkgVersion, pyVersion=None, md5Digest=None,
        testing=True, raiseError=True):
        """Fetch a spider package from a pypi server and install them"""

    def removePackage(pkgName, pkgVersion, pyVersion):
        """Remove a package installed with package installer

        Note: we can't use our default python version becuaae we do not know
        if this is the version whihc get used during installation.
        """

    def listPackages():
        """Returns a list of installed packages, versions and spiders"""

    def listAllSpiders():
        """Returns a list of spiders now.
        
        Note: this method is by passing the queue and uses the server thread

        """

    def listSpiders(pkgName, pkgVersion, pyVersion):
        """Returns a list of spiders"""

    def runSpider(pkgName, pkgVersion, pyVersion, spiderName, cmdOption=None):
        """Run a specific spider now.
        
        Note: this method is by passing the queue and uses the server thread

        """

    # shared remote processor job API, this means we can talk to one server
    # an add jobs restricted to our or other servers
    def startAddPackage(pkgName, pkgVersion, pyVersion=None, md5Digest=None,
        testing=True):
        """Add a AddPackage job and return a dict of serverName:jobid as result.

        """


    def startRunSpider(pkgName, pkgVersion, pyVersion, spiderName,
        cmdOption=None):
        """Add one RunSpider job for run a specific spider package
        on our server.
        
        Optional you can use cmdOptions which get added to the crawl command
        e.g.:
        
          bin/buildout scpray crawl <cmdOptions>

        or as a real example:
        
          bin/buildout scrapy crawl --nolog --test
        
        """

    def startSyncPackages(sourceServerName, testing=False):
        """Add a SyncPackages job and return the jobid"""


# package manager
class IPackageManager(zope.interface.Interface):
    """Scrapy spider package installer"""

    def add(pypiURL, pkgName, version, testing=True, md5Digest=None):
        """Install a package to the given location.
        
        Use the following authentication pattern if you need authentication:
        
        http://username:password@domain/pypi/pkg/version/file#checksum

        """
    def remove(pkgName, version):
        """Remove a package installed with package installer"""


# publisher
class IScrapyRequest(z3c.jsonrpc.interfaces.IJSONRPCRequest):
    """Scrapy JSON-RPC request."""

    root = zope.interface.Attribute("""IScrapyRoot instance""")


class IScrapyPublication(z3c.jsonrpc.interfaces.IJSONRPCPublication):
    """Scrapy JSON-RPC publication."""

    root = zope.interface.Attribute("""IScrapyRoot instance""")

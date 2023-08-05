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
"""Scrapy JSON-RPC package and spider management methods
$Id:$
"""
__docformat__ = "reStructuredText"

import time

from z3c.jsonrpc.publisher import MethodPublisher

import s01.core.mongo


class ScrapyMethods(MethodPublisher):
    """ScrapyRoot JSON-RPC methods"""

    # server
    def getStartTime(self):
        """Returns server start time"""
        return self.context.getStartTime()

    def getMongoDBStatus(self):
        pool = s01.core.mongo.mongoConnectionPool
        try:
            con = pool.connection
            status = {'status': True, 'host': con.host, 'port': con.port}
        except Exception, e: # we will never fail
            status = {'status': False, 'host': pool.host, 'port': pool.port}
        return status

    # remote processor
    def getProcessorStartTime(self):
        """Returns processor start time"""
        return self.context.getProcessorStartTime()

    def startProcessor(self):
        self.context.startProcessor()
        time.sleep(0.5)
        return self.context.isProcessing

    def stopProcessor(self):
        self.context.stopProcessor()
        time.sleep(0.5)
        return self.context.isProcessing

    def isProcessing(self):
        return self.context.isProcessing

    # server internals
    def getDefaultPythonVersion(self):
        """Returns the defaul python version"""
        return self.context.defaultPythonVersion

    def getPythonVersions(self):
        """Returns all (available) python version"""
        return self.context.pythonVersions

    # buildout package management
    def addPackage(self, pkgName, pkgVersion, pyVersion=None, md5Digest=None,
        testing=True):
        """Fetch a package from a pypi server and install them"""
        # do not raise error, catch them and return errors in result data
        raiseError = False
        return self.context.addPackage(pkgName, pkgVersion, pyVersion,
            md5Digest, testing, raiseError)

    def removePackage(self, pkgName, pkgVersion, pyVersion):
        """Remove a package installed with package installer

        Note: we can't use our default python version becuaae we do not know
        if this is the version which get used during installation.
        """
        return self.context.removePackage(pkgName, pkgVersion, pyVersion)

    def listAllSpiders(self):
        """Returns a list of spiders"""
        return self.context.listAllSpiders()

    def listSpiders(self, pkgName, pkgVersion, pyVersion):
        """Returns a list of spiders"""
        return self.context.listSpiders(pkgName, pkgVersion, pyVersion)

    def runSpider(self, pkgName, pkgVersion, pyVersion, spiderName,
        options=None):
        """Run a specific spider"""
        return self.context.runSpider(pkgName, pkgVersion, pyVersion,
            spiderName, options)

    def getMissingPackageVersions(self, serverName=None):
        """Returns a list of missing packages/version data"""
        return self.context.getMissingPackageVersions(serverName)

    # remote job API
    def startAddPackage(self, pkgName, pkgVersion, pyVersion=None,
        md5Digest=None, testing=True):
        """Starts the SyncPackages job"""
        return self.context.startAddPackage(pkgName, pkgVersion, pyVersion,
            md5Digest, testing)

    def startRunSpider(self, pkgName, pkgVersion, pyVersion, spiderName,
        cmdOption=None):
        """Start the RunSpider job for a specific spider"""
        return self.context.startRunSpider(pkgName, pkgVersion, pyVersion,
            spiderName, cmdOption)

    def startSyncPackages(self, sourceServerName, testing=False):
        """Starts the SyncPackages job"""
        return self.context.startSyncPackages(sourceServerName, testing)

    # remote job status API
    def getJobStatus(self, jobid):
        """Returns the status of a given job"""
        return self.context.getJobStatus(jobid)

    def countJobs(self, status=None):
        """Returns the amount of all jobs or for a given status"""
        return self.context.countJobs(status)

    def removeJobs(self, stati=None):
        """See interfaces.IRemoteProcessor"""
        return self.context.removeJobs(stati)

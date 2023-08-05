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

import thread
import time

import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty

import m01.remote.interfaces
import m01.mongo.base
import m01.remote.processor
import m01.remote.worker

import s01.core.package
import s01.core.job
import s01.core.mongo
from s01.worker import interfaces
from s01.worker import util
from s01.worker import package


class ScrapyRoot(m01.mongo.base.MongoStorageBase,
    m01.remote.processor.RemoteProcessor):
    """Scrapy worker (application root)"""

    zope.interface.implements(interfaces.IScrapyRoot)

    __name__ = __parent__ = None

    title = u'ScrapyRoot'
    start_time = None
    
    serverName = FieldProperty(interfaces.IScrapyRoot['serverName'])
    pkgsDir = FieldProperty(interfaces.IScrapyRoot['pkgsDir'])
    pypiURL = FieldProperty(interfaces.IScrapyRoot['pypiURL'])
    pythonVersions = FieldProperty(interfaces.IScrapyRoot['pythonVersions'])

    def __init__(self, serverName, pkgsDir, pypiURL, defaultPythonVersion,
        jobWorkerMaxThreads, jobWorkerWaitTime):
        # don't call any super class, setup everything here
        # setup storages using mongodb collections
        self._jobFactories = m01.remote.job.JobFactories(self)
        self._jobFactories.__parent__ = self
        self._jobs = m01.remote.job.Jobs(self)
        self._jobs.__parent__ = self
        self.start_time = time.time()
        self.serverName = serverName
        self.pkgsDir = pkgsDir
        self.pypiURL = pypiURL
        self.defaultPythonVersion = defaultPythonVersion
        self.jobWorkerMaxThreads = jobWorkerMaxThreads
        self.jobWorkerWaitTime = jobWorkerWaitTime
        # will be set during startup, see buildout.cfg
        self.pythonVersions = {}

    # processor internals
    @property
    def jobWorkerFactory(self):
        if self.jobWorkerMaxThreads == 1:
            return m01.remote.worker.SimpleJobWorker
        else:
            return m01.remote.worker.MultiJobWorker

    @property
    def jobWorkerArguments(self):
        return {'jobQuery': {'serverNames': self.serverName},
                'waitTime': self.jobWorkerWaitTime,
                'maxThreads': self.jobWorkerMaxThreads}

    # m01.mongo internals
    @property
    def collection(self):
        """Returns a thread local shared collection."""
        return s01.core.mongo.getScrapyPackages()

    @property
    def cacheKey(self):
        return 's01.packages.%i' % thread.get_ident()

    # restrict ScrapyPackage items to this server
    def doFilter(self, spec):
        """Only use ScrapyPackage items added by this server"""
        spec['serverName'] = self.serverName
        return spec

    def load(self, data):
        """Load data into the relevant item type"""
        _type = data.get('_type')
        if _type == 'ScrapyPackage':
            return s01.core.package.ScrapyPackage(data)
        else:
            raise TypeError("No class found for mongo _type %s" % _type)
    

    # jobFactory management API
    def ensureJobFactories(self):
        """Installs all job factories if not allready available"""
        # ensure RunSpider job
        commitRequired = False
        msgs = []
        jobFactories = [(u'RunSpider', s01.core.job.RunSpider),
                        (u'AddPackage', s01.core.job.AddPackage),
                        (u'SyncPackages', s01.core.job.SyncPackages),]
        for name, factory in jobFactories:
            if not self._jobFactories.__contains__(name):
                obj = factory()
                self.addJobFactory(name, obj)
                msgs.append('Remote processor job %s installed' % name)
                commitRequired = True
            else:
                msgs.append('Remote processor job %s available' % name)
        return msgs, commitRequired

    @property
    def _scheduler(self):
        """There is no scheduler installed"""
        raise NotImplementedError(
            "The ScrapyRoot doesn't support a scheduler")

    # ISite
    def getStartTime(self):
        return self.start_time

    def getProcessorStartTime(self):
        """Returns the processor start time"""
        return self.processorStartTime

    def getSiteManager(self):
        return zope.component.getGlobalSiteManager()

    def setSiteManager(self, sm):
        raise NotImplementedError("setSiteManager is not supported")

    # IRemoteProcessor
    def getRemoteProcessorJobFactoryCollection(self):
        """Returns the mongodb job factory collection"""
        return s01.core.mongo.getRemoteFactories()

    def getRemoteProcessorJobCollection(self):
        """Returns the mongodb job collection"""
        return s01.core.mongo.getRemoteJobs()

    def getRemoteProcessorSchedulerCollection(self):
        """This implementation provides a scheduler an remote processor"""
        raise NotImplementedError("The ScrapyRoot doesn't support a scheduler")

    def loadRemoteProcessorJobItems(self, data):
        """Load data into the relevant item type"""
        _type = data.get('_type')
        if _type == 'RunSpider':
            obj = s01.core.job.RunSpider(data)
        elif _type == 'AddPackage':
            obj = s01.core.job.AddPackage(data)
        elif _type == 'SyncPackages':
            obj = s01.core.job.SyncPackages(data)
        else:
            raise TypeError("No class found for mongo _type %s" % _type)
        return obj

    # scheduler API (not implemented/supported)
    def addScheduler(self, item):
        """Add a new scheduler item."""
        raise NotImplementedError("Does not support the scheduler API")

    def scheduleNextJob(self, callTime=None):
        """Schedule next job"""
        raise NotImplementedError("Does not support the scheduler API")

    def reScheduleItem(self, item, callTime=None):
        """Re-schedule an item"""
        raise NotImplementedError("Does not support the scheduler API")

    def reScheduleItems(self, callTime=None):
        """Re-schedule all items"""
        raise NotImplementedError("Does not support the scheduler API")

    # ScrapyPackage management API used by package manager
    def doEnsureScrapyPackage(self, pkgName, pkgVersion, pyVersion, md5Digest,
        spiderNames):
        """Ensures that a package and version is stored in the mongodb."""
        # find existing package, should not exist but who knows
        data = {'serverName': self.serverName,
                'pkgName': pkgName,
                'pkgVersion': pkgVersion,
                'pyVersion': pyVersion}
        if not self.doCount(self.collection, data):
            # now we can add our md5 digest and spider names
            data['md5Digest'] = md5Digest
            data['spiderNames'] = spiderNames
            # add the package
            pkg = s01.core.package.ScrapyPackage(data)
            return self.add(pkg)
        return None

    def doRemoveScrapyPackage(self, pkgName, pkgVersion, pyVersion):
        """Remove an existing ScrapyPackage"""
        data = {'serverName': self.serverName,
                'pkgName': pkgName,
                'pkgVersion': pkgVersion,
                'pyVersion': pyVersion}
        data = self.doFindOne(self.collection, data)
        if data is not None:
            del self[data['__name__']]
            return True
        return False

    # buildout package management API
    def queryPackage(self, pkgName, pkgVersion, pyVersion):
        """Returns a package for given pkgName and pkgVersion or None"""
        data = self.collection.find_one({'pkgName':pkgName ,
                                         'pkgVersion':pkgVersion,
                                         'pyVersion': pyVersion})
        if data is not None:
            return self.doLoad(data)

    def hasPackage(self, pkgName, version):
        """Retruns True or False if a package version is given"""
        return package.getPackageDir(self.pkgsDir, pkgName, version)

    def getMissingPackageVersions(self, serverName=None):
        """Returns a list of missing packages/version data compared to another
        server by it's serverName.
        """
        data = []
        if serverName is None:
            serverName = self.serverName
        spec = {'_type': 'ScrapyPackage', 'serverName': serverName}
        for d in self.collection.find(spec):
            pkgName = d['pkgName']
            pkgVersion = d['pkgVersion']
            if not self.hasPackage(pkgName, pkgVersion):
                # the data get used as InstallPackage job input
                data.append({'pkgName': pkgName, 'pkgVersion': pkgVersion})
        return data

    def addPackage(self, pkgName, pkgVersion, pyVersion=None, md5Digest=None,
        testing=True, raiseError=True):
        """Fetch a spider package from a pypi server and install them"""
        if pyVersion is None:
            pyVersion = self.defaultPythonVersion
        manager = interfaces.IPackageManager(self)
        try:
            # add the crawler package in our package location
            return manager.doAddPackage(pkgName, pkgVersion, pyVersion,
                md5Digest, testing, raiseError)
        except Exception, e:
            if raiseError:
                # raise exception, only used if not called by JSON-RPC
                raise e
            else:
                # catch unhandled exceptions and return them as json data,
                # this is used in JSON-RPC API where we don't raise exceptions
                return {'status': False, 'error': str(e)}

    def removePackage(self, pkgName, pkgVersion, pyVersion):
        """Remove a package installed with package installer

        Note: we can't use our default python version becuaae we do not know
        if this is the version which get used during installation.
        """
        # setup installer
        manager = interfaces.IPackageManager(self)
        try:
            # remove package
            return manager.doRemovePackage(pkgName, pkgVersion, pyVersion)
        except Exception, e:
            # catch unhandled exceptions
            return {'status': False, 'error': str(e)}

    def listAllSpiders(self):
        """Returns a list of spiders now.
        
        Note: this method is by passing the queue and uses the server thread

        """
        manager = interfaces.IPackageManager(self)
        try:
            pkgs = manager.listAllSpiders()
            return {'pkgs': pkgs, 'error': None}
        except Exception, e:
            # catch unhandled exceptions
            return {'pkgs': {}, 'error': str(e)}

    def listSpiders(self, pkgName, pkgVersion, pyVersion):
        """Returns a list of spiders"""
        manager = interfaces.IPackageManager(self)
        try:
            return manager.listSpiders(pkgName, pkgVersion, pyVersion)
        except Exception, e:
            # catch unhandled exceptions
            return {'spiders': [], 'error': str(e)}

    def runSpider(self, pkgName, pkgVersion, pyVersion, spiderName,
        cmdOption=None, raiseError=True):
        """Run a specific spider now.
        
        Note: this method is by passing the queue and uses the server thread

        """
        # check if we know this spider
        pkg = self.queryPackage(pkgName, pkgVersion, pyVersion)
        if pkg is None:
            msg = "Package (%s %s %s) not available" % (pkgName, pkgVersion,
                pyVersion)
            if raiseError:
                raise ValueError(msg)
            else:
                return {'status': False, 'error': msg}
        elif spiderName not in pkg.spiderNames:
            msg = u'Spider name (%s) not available in spiderNames' % spiderName
            if raiseError:
                raise ValueError(msg)
            else:
                return {'status': False, 'error': msg}
        else:
            manager = interfaces.IPackageManager(self)
            try:
                return manager.doRunSpider(pkgName, pkgVersion, pyVersion,
                    spiderName, cmdOption, raiseError)
            except Exception, e:
                if raiseError:
                    # raise exception, only used if not called by JSON-RPC
                    raise e
                else:
                    # catch unhandled exceptions and return them as json data,
                    # this is used in JSON-RPC API where we don't raise exceptions
                    status = {'status': False, 'error': str(e)}
                    return status

    # shared remote processor job API, this means we can talk to one server
    # and add jobs restricted to our or other servers
    def startAddPackage(self, pkgName, pkgVersion, pyVersion=None,
        md5Digest=None, testing=True):
        """Add one or more AddPackage job based on the given serverNames
        and return a dict of serverName:jobid as result.
        
        The serverNames value could be None, a single serverName as string or a
        list of serverName. If Non is given, we will restrict the AddPackage
        job to this server by using our serverName.
        """
        if pyVersion is None:
            pyVersion = self.defaultPythonVersion
        data = {'serverNames': [self.serverName],
                'pkgName': pkgName,
                'pkgVersion': pkgVersion,
                'pyVersion': pyVersion,
                'md5Digest': md5Digest,
                'testing': testing}
        # add job and return jobid
        return self.addJob('AddPackage', data)

    def startRunSpider(self, pkgName, pkgVersion, pyVersion, spiderName,
        cmdOption=None):
        """Add RunSpider job and return jobid
        
        Optional you can use cmdOptions which get added to the crawl command
        e.g.:
        
          bin/buildout scpray crawl <cmdOptions>

        or as a real example:
        
          bin/buildout scrapy crawl --nolog --test

        """
        # check if we know this spider
        pkg = self.queryPackage(pkgName, pkgVersion, pyVersion)
        if pkg is None:
            return {'status': False, 'error': u'Package not available'}
        elif spiderName not in pkg.spiderNames:
            return {'status': False, 'error':
                    u'Spider name not available in spiderNames'}
        else:
            # add one job for all given serverNames
            data = {'serverNames': [self.serverName],
                    'pkgName': pkgName,
                    'pkgVersion': pkgVersion,
                    'pyVersion': pyVersion,
                    'spiderName': spiderName,
                    'cmdOption': cmdOption}
            return self.addJob('RunSpider', data)

    def startSyncPackages(self, sourceServerName, testing=False):
        """Add a SyncPackages job and return the jobid"""
        data = {'serverNames': [self.serverName],
                'sourceServerName': sourceServerName,
                'testing': testing}
        return self.addJob('SyncPackages', data)

    def countJobs(self, status=None):
        collection = self._jobs.collection
        doCount = self._jobs.doCount
        if status is not None:
            data = doCount(collection, {'status': status})
        else:
            data = {}
            for status in m01.remote.interfaces.JOB_STATUS_NAMES:
                data[status] = doCount(collection, {'status': status})
        return data

    def removeJobs(self, stati=None):
        """See interfaces.IRemoteProcessor"""
        try:
            res = super(ScrapyRoot, self).removeJobs(stati)
            status = {'status': True, 'result': res, 'error': None}
        except ValueError, e:
            status = {'status': False, 'error': str(e)}
        return status

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)


scrapyRoot = ScrapyRoot(util.serverName, util.pkgsDir, util.pypiURL,
    util.defaultPythonVersion, util.jobWorkerMaxThreads, util.jobWorkerWaitTime)

# auto start processor
if util.autoStartProcessor:
    scrapyRoot.startProcessor()


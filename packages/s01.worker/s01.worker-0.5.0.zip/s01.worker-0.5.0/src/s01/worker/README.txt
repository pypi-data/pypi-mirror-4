==============
Scrapy JSONRPC
==============

This package provides a web application server which can act as a scrapy deamon
like scarpyd. We do not use scrapyd in any way, we use our own remote processing
library called m01.remote. This application also supports a JSON-RPC 2.0 API 
which can be used for adding spiders etc. And the package also offers built-in
security settings.

By default this application server also runs on port 6800 like the original
scrapyd deamon.

NOTE: we do not support running scrapy spiders out of the box. Scrapy spiders
must provide a buildout based setup. See s01.demo for a sample package which 
depends on s01.scrapy. An important requirment is that the spider package must
provide a worker.cfg file with a crawl buildout part.

The s01.scrapy based spider package provides the following command:

  bin/crawl <spider-name>

Also check our test package in src/s01/worker/testing/pypi

Let's start testing and install a log handler:

  >>> from pprint import pprint
  >>> import time
  >>> import transaction
  >>> import m01.mongo.testing
  >>> import s01.core.mongo
  >>> import s01.worker.testing

  >>> from zope.testing import loggingsupport
  >>> logger = loggingsupport.InstalledHandler('s01.worker')


ScrapyRoot
----------

The ScrapyRoot item is used as a non persistent application root and can get
traversed. This ScrapyRoot item also provides a container where we can store
ScrapyPackage. Such ScrapyPackage items will get stored in the mongodb. We 
use the m01.mongo package for mongodb object mapping.

Let's test the ScrapyRoot:

  >>> root = getRootFolder()
  >>> root
  <ScrapyRoot>

This scarpy root item comes from our root.py module:

  >>> import s01.worker.root
  >>> scrapyRoot = s01.worker.root.scrapyRoot
  >>> scrapyRoot
  <ScrapyRoot>

  >>> root is scrapyRoot
  True


JSON-RPC
--------

The JSON server looks for content-type "application/json", and handles those
requests as JSON-RPC. We can use this JSON-RPC server with a JSON-RPC 2.0 
aware client like the one given from z3c.jsonrpc or s01.client.

We used our ScrapyTestProxy for testing. This JSON-RPC proxy is a wrapper
for the original JSONRPCProxy and adds handleErrors support and a special
Transport layer which uses a testing caller. You can use the 
BasicAuthTransport Transport layers defined in the z3c.json.transport module
in real usecases together with the default JSONRPCProxy implementation. If you
don't like to use the built-in authentication, you must register the JSONRPC
methods within the zope.Public permission. Then you can use the JSONRPCProxy
with the default transport layer without authentication.

  >>> serverURL = 'http://localhost/++skin++Scrapy'
  >>> proxy = s01.worker.testing.ScrapyTestProxy(serverURL, 'mgr', 'mgrpw')
  >>> proxy.handleErrors = False

Let's the the API meethods


getStartTime
~~~~~~~~~~~~

  >>> startTime = proxy.getStartTime()
  >>> startTime > 1289184237
  True


getMongoDBStatus
~~~~~~~~~~~~~~~~

  >>> proxy.getMongoDBStatus()
  {u'status': True, u'host': u'localhost', u'port': 45017}


getProcessorStartTime
~~~~~~~~~~~~~~~~~~~~~

  >>> proxy.getProcessorStartTime() is None
  True


startProcessor
~~~~~~~~~~~~~~

  >>> proxy.isProcessing()
  False

  >>> proxy.startProcessor()
  True

  >>> proxy.isProcessing()
  True


stopProcessor
~~~~~~~~~~~~~

  >>> proxy.stopProcessor()
  False

  >>> proxy.isProcessing()
  False


isProcessing
~~~~~~~~~~~~

  >>> proxy.isProcessing()
  False


getDefaultPythonVersion
~~~~~~~~~~~~~~~~~~~~~~~

The default python version is the python version which the shell returns. 
And we only use the first two parts from the full version as an unicode string.
e.g. u'2.6'. See getShellPythonVersion in s01/worker/util.py. Let's get the
current version:

  >>> import sys
  >>> vi = sys.version_info
  >>> v = '%i.%i' % (vi[0], vi[1])

  >>> proxy.getDefaultPythonVersion() == v
  True


getPythonVersions
~~~~~~~~~~~~~~~~~

We can set different python versions by define a python version and path as
key/value. Such python versions can be used to execute the spider package.
This means our server can get installed with python 2.6 and can execute 
the spiders with python 2.5 oder 3.1. This means only the referenced python
version used for a spider must provide what the spider needs and not the
s01.worker application server.

As you can see in our buildout.cfg file (s01.worker top level folder). You can
simply use the product config for define our own pyhton versions. You can even
use custom keys for reference a python installation. Currently we support
the follwong product config section:

  - win32
  - linux2
  - darwin

This names are the same as 

  <pythonversions win32>
    2.5.4 C:/Python25/python.exe
    2.6.6 C:/Python26/python.exe
    2.7 C:/Python27/python.exe
    2.6-with-openssl C:/Python26OpenSSL/python.exe
  </pythonversions>
  <pythonversions linux2>
    2.5.4 /usr/bin/python
    2.6.6 /usr/local/bin/python26
    2.7 /usr/local/bin/python27
    2.6-with-openssl /usr/local/bin/python26OpenSSL
  </pythonversions>

You can reference such python version in our addPackage method:

  pkgName = u's01.demo'
  pkgVersion = u'0.16.2'
  pyVersion = u'2.6-with-openssl'
  scrapyRoot.addPackage(pkgName, pkgVersion, pyVersion)


Let's test the pythonVersions. Note, we normaly do not manage python versions.
The python version setup should be done in the buildout.cfg.:

  >>> proxy.getPythonVersions()
  {}

Let's show how we can define additional python versions. Such python versions
are availble for add and execute spider packages by using it's key:

  >>> scrapyRoot.pythonVersions
  {}

  >>> scrapyRoot.pythonVersions['42.0'] = '/path/to/python'
  >>> scrapyRoot.pythonVersions
  {'42.0': '/path/to/python'}

As you can see, we can get the pyton versions with our JSON-RPC client:

  >>> proxy.getPythonVersions()
  {u'42.0': u'/path/to/python'}

Let's remove this junk:

  >>> del scrapyRoot.pythonVersions['42.0']
  >>> scrapyRoot.pythonVersions
  {}


addPackage
~~~~~~~~~~

Check our logger which must be empty yet:

  >>> print logger

  >>> pkgName = u's01.demo'
  >>> pkgVersion = u'0.16.2'
  >>> pyVersion = None
  >>> md5Digest = None
  >>> testing = False
  >>> raiseError = True
  >>> res = proxy.addPackage(pkgName, pkgVersion, pyVersion, md5Digest,
  ...     testing)

We need to commit that mongo transaction writes the package to the db:

  >>> transaction.commit()

  >>> pprint(res)
  {u'error': None,
   u'spiders': [u'python.org'],
   u'status': True,
   u'steps': [{u'msg': {u'pkgName': u's01.demo',
                      u'pkgVersion': u'0.16.2',
                      u'pypiURL': u'http://pypi.python.org/pypi'},
              u'step': u'fetch'},
             {u'msg': u'http://pypi.python.org/packages/source/s01.demo/s01.demo-0.16.2.zip',
              u'step': u'download'},
             {u'msg': u'...',
              u'step': u'unpack'},
             {u'msg': u'...', u'step': u'unpack'},
             {u'msg': u'...',
              u'step': u'unpack move'},
             {u'msg': u"Creating directory ...",
              u'step': u'bootstrap'},
             {u'msg': u"Develop: ...",
              u'step': u'buildout'},
             {u'msg': u'...',
              u'step': u'list'},
             {u'msg': u's01.demo 0.16.2', u'step': u'ensureScrapyPackage'}]}

Check the logger:

  >>> s01.worker.testing.reNormalizer.pprint(logger)
  s01.worker INFO
    fetch: {'pkgVersion': u'0.16.2', 'pkgName': u's01.demo', 'pypiURL': 'http:/pypi.python.org/pypi'}
  s01.worker INFO
    download: http:/pypi.python.org/packages/source/s01.demo/s01.demo-0.16.2.zip
  s01.worker INFO
    unpack: ...-pkgs/s01.demo/0.16.2/2.7
  s01.worker INFO
    unpack: ...
  s01.worker INFO
    unpack move: ...-pkgs/s01.demo/0.16.2/2.7
  s01.worker INFO
    bootstrap: Creating directory ...-pkgs/s01.demo/0.16.2/2.7/bin'.
  Creating directory ...-pkgs/s01.demo/0.16.2/2.7/parts'.
  Creating directory ...-pkgs/s01.demo/0.16.2/2.7/develop-eggs'.
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/buildout'.
  s01.worker INFO
    buildout: Develop: ...-pkgs/s01.demo/0.16.2/2.7/.'
  Installing tmp.
  tmp: Creating directory ...
  Installing log.
  log: Creating directory ...
  Installing settings.
  s01.worker: Creating directory ...-pkgs/s01.demo/0.16.2/2.7/parts/settings
  s01.worker: Writing file ...-pkgs/s01.demo/0.16.2/2.7/parts/settings/default.cfg
  s01.worker: Change mode ... for ...-pkgs/s01.demo/0.16.2/2.7/parts/settings/default.cfg
  Installing list.
  s01.worker: Load settings given from section target ...-pkgs/s01.demo/0.16.2/2.7/parts/settings/default.cfg
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/list'.
  Installing crawl.
  s01.worker: Load settings given from section target ...-pkgs/s01.demo/0.16.2/2.7/parts/settings/default.cfg
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/crawl'.
  Installing scrapy.
  s01.worker: Load settings from path ...-pkgs/s01.demo/0.16.2/2.7/parts/settings/default.cfg
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/scrapy'.
  Installing crawl-settings-file.
  s01.worker: Load settings from path ...-pkgs/s01.demo/0.16.2/2.7/parts/settings/default.cfg
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/crawl-settings-file'.
  Installing crawl-settings-and-overrides.
  s01.worker: Load settings from path ...-pkgs/s01.demo/0.16.2/2.7/parts/settings/default.cfg
  s01.worker: Load overrides
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/crawl-settings-and-overrides'.
  Installing crawl-overrides.
  s01.worker: Load overrides
  s01.worker: Enable testing option
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/crawl-overrides'.
  Installing crawl-non-spider.
  s01.worker: Load settings from path ...-pkgs/s01.demo/0.16.2/2.7/parts/settings/default.cfg
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/crawl-non-spider'.
  Installing test.
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/test'.
  Installing coverage-test.
  Generated script ...-pkgs/s01.demo/0.16.2/2.7/bin/coverage-test'.
  Installing coverage-report.
  s01.worker INFO
    list: ...-pkgs/s01.demo/0.16.2/2.7
  s01.worker INFO
    ensureScrapyPackage: s01.demo 0.16.2

As you can see, we will get an error if we try again to add the same package:

  >>> res = scrapyRoot.addPackage(pkgName, pkgVersion, pyVersion, md5Digest,
  ...     testing, raiseError)
  Traceback (most recent call last):
  ...
  JobError: Duplicated Package found at: ...

  >>> logger.clear()


listAllSpiders
~~~~~~~~~~~~~~

Returns a list of spiders:

  >>> pprint(proxy.listAllSpiders())
  {u'error': None,
   u'pkgs': {u's01.demo': {u'0.16.2': {u'2.7': {u'code': 0,
                                                u'error': None,
                                                u'spiders': [u'python.org']}}}}}


listSpiders
~~~~~~~~~~~

Returns a list of spiders:

  >>> pyVersion = scrapyRoot.defaultPythonVersion
  >>> pprint(proxy.listSpiders(pkgName, pkgVersion, pyVersion))
  {u'code': 0, u'error': None, u'spiders': [u'python.org']}


runSpider
~~~~~~~~~

Run a specific spider:

  >>> siderName = 'python.org'
  >>> pprint(proxy.listSpiders(pkgName, pkgVersion, pyVersion))
  {u'code': 0, u'error': None, u'spiders': [u'python.org']}


getMissingPackageVersions
~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a list of missing packages/version data:

  >>> serverName = None
  >>> pprint(proxy.getMissingPackageVersions(serverName))
  []


removePackage
~~~~~~~~~~~~~

Remove a package installed with package installer:

  >>> serverName = None
  >>> pprint(proxy.removePackage(pkgName, pkgVersion, pyVersion))
  {u'error': None,
   u'status': True,
   u'steps': [{u'msg': u'...',
               u'step': u'exists'},
              {u'msg': u'...',
               u'step': u'rmtree'},
              {u'msg': u's01.demo 0.16.2 ...',
               u'step': u'doRemoveScrapyPackage'}]}

Let's commit the remove transaction:

  >>> transaction.commit()


startAddPackage
~~~~~~~~~~~~~~~

Now we start using the remote processor API. First we need to make sure that we
have the jobs available. We can do this by calling ensureJobFactories:

  >>> pprint(scrapyRoot.ensureJobFactories())
  ([u'Remote processor job RunSpider installed',
    u'Remote processor job AddPackage installed',
    u'Remote processor job SyncPackages installed'],
   True)

Start the remote processor

  >>> proxy.startProcessor()
  True

  >>> proxy.isProcessing()
  True

And start adding a AddPackage remote job:

  >>> pprint(proxy.startAddPackage(pkgName, pkgVersion, pyVersion))
  u'...'

commit:

  >>> transaction.commit()

  >>> remoteJobs = s01.core.mongo.getRemoteJobs()
  >>> m01.mongo.testing.reNormalizer.pprint(remoteJobs.find())
  {u'__name__': u'...',
   u'_id': ObjectId('...'),
   u'_type': u'AddPackage',
   u'_version': 1,
   u'active': True,
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'errors': [],
   u'jobName': u'AddPackage',
   u'maxRetries': 3,
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'pkgName': u's01.demo',
   u'pkgVersion': u'0.16.2',
   u'pyVersion': u'...',
   u'queued': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'retryCounter': 0,
   u'retryDelay': 300,
   u'serverNames': [u'testing'],
   u'status': u'queued',
   u'testing': True}

and give some time to install the package and check again:

  >>> time.sleep(90)
  >>> m01.mongo.testing.reNormalizer.pprint(remoteJobs.find())
  {u'__name__': u'...',
   u'_id': ObjectId('...'),
   u'_type': u'AddPackage',
   u'_version': 2,
   u'active': True,
   u'completed': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'errors': [],
   u'jobName': u'AddPackage',
   u'maxRetries': 3,
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'output': {u'error': None,
               u'spiders': [u'python.org'],
               u'status': True,
               u'steps': [{u'msg': {u'pkgName': u's01.demo',
                                    u'pkgVersion': u'0.16.2',
                                    u'pypiURL': u'http://pypi.python.org/pypi'},
                           u'step': u'fetch'},
                          {u'msg': u'http://pypi.python.org/packages/source/s01.demo/s01.demo-0.16.2.zip',
                           u'step': u'download'},
                          {u'msg': u'...',
                           u'step': u'unpack'},
                          {u'msg': u'...',
                           u'step': u'unpack'},
                          {u'msg': u'...',
                           u'step': u'unpack move'},
                          {u'msg': u"Creating directory ...",
                           u'step': u'bootstrap'},
                          {u'msg': u"Develop: ...",
                           u'step': u'buildout'},
                          {u'msg': u'Total: 0 tests, 0 failures, 0 errors in 0.000 seconds.\r\n',
                           u'step': u'test'},
                          {u'msg': u'...',
                           u'step': u'list'},
                          {u'msg': u's01.demo 0.16.2',
                           u'step': u'ensureScrapyPackage'}]},
   u'picked': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'pkgName': u's01.demo',
   u'pkgVersion': u'0.16.2',
   u'pyVersion': u'...',
   u'queued': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'retryCounter': 1,
   u'retryDelay': 300,
   u'retryTime': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'serverNames': [u'testing'],
   u'started': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'status': u'completed',
   u'testing': True}

startRunSpider
~~~~~~~~~~~~~~

Start the RunSpider job for a specific spider:

  >>> pprint(proxy.startRunSpider(pkgName, pkgVersion, pyVersion, siderName))
  u'...'

And commit again:

  >>> transaction.commit()
  >>> time.sleep(30)

  >>> m01.mongo.testing.reNormalizer.pprint(remoteJobs.find())
  {u'__name__': u'...',
   u'_id': ObjectId('...'),
   u'_type': u'AddPackage',
   u'_version': 2,
   u'active': True,
   u'completed': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'errors': [],
   u'jobName': u'AddPackage',
   u'maxRetries': 3,
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'output': {u'error': None,
               u'spiders': [u'python.org'],
               u'status': True,
               u'steps': [{u'msg': {u'pkgName': u's01.demo',
                                    u'pkgVersion': u'0.16.2',
                                    u'pypiURL': u'http://pypi.python.org/pypi'},
                           u'step': u'fetch'},
                          {u'msg': u'http://pypi.python.org/packages/source/s01.demo/s01.demo-0.16.2.zip',
                           u'step': u'download'},
                          {u'msg': u'...',
                           u'step': u'unpack'},
                          {u'msg': u'...',
                           u'step': u'unpack'},
                          {u'msg': u'...',
                           u'step': u'unpack move'},
                          {u'msg': u"Creating directory ...",
                           u'step': u'bootstrap'},
                          {u'msg': u"Develop: ...",
                           u'step': u'buildout'},
                          {u'msg': u'Total: 0 tests, 0 failures, 0 errors in 0.000 seconds.\r\n',
                           u'step': u'test'},
                          {u'msg': u'...',
                           u'step': u'list'},
                          {u'msg': u's01.demo 0.16.2',
                           u'step': u'ensureScrapyPackage'}]},
   u'picked': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'pkgName': u's01.demo',
   u'pkgVersion': u'0.16.2',
   u'pyVersion': u'...',
   u'queued': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'retryCounter': 1,
   u'retryDelay': 300,
   u'retryTime': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'serverNames': [u'testing'],
   u'started': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'status': u'completed',
   u'testing': True}
  {u'__name__': u'...',
   u'_id': ObjectId('...'),
   u'_type': u'RunSpider',
   u'_version': 2,
   u'active': True,
   u'completed': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'errors': [],
   u'jobName': u'RunSpider',
   u'maxRetries': 3,
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'output': {u'code': 0, u'error': u'', u'status': True},
   u'picked': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'pkgName': u's01.demo',
   u'pkgVersion': u'0.16.2',
   u'pyVersion': u'...',
   u'queued': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'retryCounter': 1,
   u'retryDelay': 300,
   u'retryTime': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'serverNames': [u'testing'],
   u'spiderName': u'python.org',
   u'started': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'status': u'completed'}


startSyncPackages
~~~~~~~~~~~~~~~~~

Add a SyncPackages job and return the jobid:

  >>> sourceServerName = u'other'
  >>> jobid = proxy.startSyncPackages(sourceServerName)
  >>> jobid
  u'...'

And commit again:

  >>> transaction.commit()

Note: this call was adding a SyncPackages remote processor job for another
server. We currently have no other server running. So let's just check if the
job get added for the other server:

  >>> m01.mongo.testing.reNormalizer.pprint(remoteJobs.find())
  {u'__name__': u'...',
   u'_id': ObjectId('...'),
   u'_type': u'AddPackage',
   u'_version': 2,
   u'active': True,
   u'completed': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'errors': [],
   u'jobName': u'AddPackage',
   u'maxRetries': 3,
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'output': {u'error': None,
               u'spiders': [u'python.org'],
               u'status': True,
               u'steps': [{u'msg': {u'pkgName': u's01.demo',
                                    u'pkgVersion': u'0.16.2',
                                    u'pypiURL': u'http://pypi.python.org/pypi'},
                           u'step': u'fetch'},
                          {u'msg': u'http://pypi.python.org/packages/source/s01.demo/s01.demo-0.16.2.zip',
                           u'step': u'download'},
                          {u'msg': u'...',
                           u'step': u'unpack'},
                          {u'msg': u'...',
                           u'step': u'unpack'},
                          {u'msg': u'...',
                           u'step': u'unpack move'},
                          {u'msg': u"Creating directory ...",
                           u'step': u'bootstrap'},
                          {u'msg': u"Develop: ...",
                           u'step': u'buildout'},
                          {u'msg': u'Total: 0 tests, 0 failures, 0 errors in 0.000 seconds.\r\n',
                           u'step': u'test'},
                          {u'msg': u'...',
                           u'step': u'list'},
                          {u'msg': u's01.demo 0.16.2',
                           u'step': u'ensureScrapyPackage'}]},
   u'picked': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'pkgName': u's01.demo',
   u'pkgVersion': u'0.16.2',
   u'pyVersion': u'...',
   u'queued': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'retryCounter': 1,
   u'retryDelay': 300,
   u'retryTime': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'serverNames': [u'testing'],
   u'started': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'status': u'completed',
   u'testing': True}
  {u'__name__': u'...',
   u'_id': ObjectId('...'),
   u'_type': u'RunSpider',
   u'_version': 2,
   u'active': True,
   u'completed': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'errors': [],
   u'jobName': u'RunSpider',
   u'maxRetries': 3,
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'output': {u'code': 0, u'error': u'', u'status': True},
   u'picked': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'pkgName': u's01.demo',
   u'pkgVersion': u'0.16.2',
   u'pyVersion': u'...',
   u'queued': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'retryCounter': 1,
   u'retryDelay': 300,
   u'retryTime': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'serverNames': [u'testing'],
   u'spiderName': u'python.org',
   u'started': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'status': u'completed'}
  {u'__name__': u'...',
   u'_id': ObjectId('...'),
   u'_type': u'SyncPackages',
   u'_version': 1,
   u'active': True,
   u'created': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'errors': [],
   u'jobName': u'SyncPackages',
   u'maxRetries': 3,
   u'modified': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'queued': datetime(..., tzinfo=<bson.tz_util.FixedOffset ...>),
   u'retryCounter': 0,
   u'retryDelay': 300,
   u'serverNames': [u'testing'],
   u'sourceServerName': u'other',
   u'status': u'queued',
   u'testing': False}


getJobStatus
~~~~~~~~~~~~

Returns the status of a given job:

  >>> pprint(proxy.getJobStatus(jobid))
  u'queued'


countJobs
~~~~~~~~~

Returns the status of a given job:

  >>> pprint(proxy.countJobs())
  {u'cancelled': 0, u'completed': 2, u'error': 0, u'processing': 0, u'queued': 1}


removeJobs
~~~~~~~~~~

Removes all jobs with the given status:

  >>> pprint(proxy.removeJobs())
  {u'error': None,
   u'result': {u'cancelled': 0, u'completed': 2, u'error': 0},
   u'status': True}


Error handling
--------------

See what happens if our JSON-RPC proxy raises an Exception. We will get a
response error with additional error content:

  >>> proxy.notAvailableMethodName()
  Traceback (most recent call last):
  ...
  ResponseError: Check proxy.error for error message

and the error content looks like:

  >>> proxy.error
  {u'message': u'Method not found', u'code': -32601, u'data': {u'i18nMessage': u'Method not found'}}


tear down
---------

stop processor:

  >>> proxy.isProcessing()
  True

  >>> proxy.stopProcessor()
  False

  >>> proxy.isProcessing()
  False

  >>> time.sleep(0.5)

uninstall logger handler:

  >>> logger.uninstall()

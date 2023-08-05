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
"""Package installer
$Id:$
"""
__docformat__ = "reStructuredText"

import urllib2
import os
import os.path
import sys
import xmlrpclib
import shutil
import tempfile
import stat
import subprocess
import logging
import setuptools.archive_util
try:  
   from hashlib import md5 
except ImportError: 
   from md5 import new as md5

import zope.interface
import zope.component

import m01.remote.exceptions

from s01.worker import interfaces
from s01.worker import pypi

is_win32 = sys.platform == 'win32'

logger = logging.getLogger('s01.worker')


def checkRO(function, path, excinfo):
    if (function == os.remove
        and excinfo[0] == WindowsError
        and excinfo[1].winerror == 5):
        # access is denied because it's a readonly file
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)


def rmtree(dirname):
    if is_win32:
        shutil.rmtree(dirname, ignore_errors=False, onerror=checkRO)
    else:
        shutil.rmtree(dirname)


class DownloadError(Exception):
    """Donwload error"""
    pass


def checkMD5(path, md5sum):
    """Tell whether the MD5 checksum of the file at path matches.

    No checksum being given is considered as good.

    """
    if md5sum is None:
        return True

    f = open(path, 'rb')
    checksum = md5()
    try:
        chunk = f.read(2**16)
        while chunk:
            checksum.update(chunk)
            chunk = f.read(2**16)
        return checksum.hexdigest() == md5sum
    finally:
        f.close()


def downloadPackage(url, md5Digest=None):
    """Fetches a release file and check md5Digest if given."""
    try:
        data = pypi.urlOpener(url).read()
    except urllib2.HTTPError, v:
        if '404' in str(v):
            raise DownloadError("404: %s" % url)
        elif '404' in str(v):
            raise DownloadError("401: %s" % url)
        raise DownloadError(
            "Couldn't download (HTTP Error): %s" % url)
    except urllib2.URLError, v:
        raise DownloadError("URL Error: %s " % url)
    except:
        raise DownloadError(
            "Couldn't download (unknown reason): %s" % url)
    if md5Digest:
        # check for md5 checksum
        data_md5 = md5(data).hexdigest()
        if md5Digest != data_md5:
            raise DownloadError(
                "MD5 sum does not match: %s / %s for release file %s" % (
                    md5Digest, data_md5, url))
    return data  


def buildCommand(cmdDir, cmd, oStr=None):
    if oStr is not None:
        return '%s %s' % (os.path.join(cmdDir, cmd), oStr)
    else:
        return os.path.join(cmdDir, cmd)

def doCommand(cmd, cwd=None, shell=False):
    stdout = subprocess.PIPE
    stderr = subprocess.PIPE
    # remove 'PYTHONPATH' from env, it could mess up our subprocess python
    # setup. This is at least the case in our test setup with bin\\list.exe
    env = os.environ
    if os.environ.get('PYTHONPATH'):
        del env['PYTHONPATH']
    p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, cwd=cwd,
        shell=shell, env=env)
    stdout, stderr = p.communicate()
    code = p.returncode
    if stderr:
        # we could still have an error if subprocess doesn't handle sys.exit
        code = 1
    return stdout, stderr, code


def unpackPackage(tmpPath, tmpDir):
    """Unpack package using setuptools"""
    to_chmod = []

    def pf(src, dst):
        if dst.endswith('.dll') or dst.endswith('.so'):
            to_chmod.append(dst)
        return dst or None

    setuptools.archive_util.unpack_archive(tmpPath, tmpDir, pf)
    for f in to_chmod:
        mode = ((os.stat(f)[stat.ST_MODE]) | 0555) & 07755
        chmod(f, mode)


def getTopLevelDir(sourceDir):
    """Returns top level package directory path"""
    for path, folders, filenames in os.walk(sourceDir):
        if 'bootstrap.py' in filenames:  
            return path


def movePackage(sourceDir, pkgDir):
    """Find top level package and move to target"""
    topDir = getTopLevelDir(sourceDir)
    shutil.move(topDir, pkgDir)


def getPackageDir(pkgsDir, project, pkgVersion):
    """Returns a package dir or None"""
    pkgDir = os.path.join(pkgsDir, project, pkgVersion)
    if os.path.exists(pkgDir):
        return pkgDir


def listSpiders(pkgDir):
    """Returns a list of spiders"""
    # run bootstrap
    if is_win32:
        fn = 'list.exe'
    else:
        fn = 'list'
    cmd = os.path.join(pkgDir, 'bin', fn)
    stdout, stderr, code = doCommand(cmd, cwd=pkgDir, shell=True)
    return unicode(stdout).splitlines(), stderr, code


def listAllSpiders(pkgsDir):
    """Returns a list of spiders from all installed packages"""
    pkgs = {}
    for pkgName in os.listdir(pkgsDir):
        pkgs.setdefault(pkgName, {})
        nDir = os.path.join(pkgsDir, pkgName)
        for pkgVersion in os.listdir(nDir):
            pkgs[pkgName].setdefault(pkgVersion, {})
            vDir = os.path.join(nDir, pkgVersion)
            for pyVersion in os.listdir(vDir):
                pkgs[pkgName][pkgVersion].setdefault(pyVersion, {})
                pkgDir = os.path.join(vDir, pyVersion)
                # run scrapy list cmd
                spiders, stderr, code = listSpiders(pkgDir)
                if not code:
                    pkgs[pkgName][pkgVersion][pyVersion] = {
                        'spiders': spiders,
                        'error': stderr and stderr or None,
                        'code': code}
                else:
                    if spiders and not stderr:
                        # output means cmd output which is an error
                        stderr = ''.join(spiders)
                    pkgs[pkgName][pkgVersion][pyVersion] = {
                        'spiders': [],
                        'error': stderr and stderr or None,
                        'code': code}
    return pkgs


def runSpider(pkgDir, spiderName, cmdOptions=None):
    """Start a specific spider from a given package location"""
    # run bootstrap
    oStr = ''
    if cmdOptions is not None:
        oStr = ' %s' % cmdOptions
    if is_win32:
        fn = 'crawl.exe'
    else:
        fn = 'crawl'
    cmd = '%s %s%s' % (os.path.join(pkgDir, 'bin', fn), spiderName, oStr)
    return doCommand(cmd, cwd=pkgDir)
    

# error helper methods
def fixError(error):
    if isinstance(error, xmlrpclib.ProtocolError):
        # eeek, this error contains our login and password in __repr__
        # located in our .pypirc
        e = 'errcode: %s, errmsg: %s' % (error.errcode, error.errmsg)
    else:
        e = str(error)
    return e 


def logError(steps, step, e, raiseError=False):
    if isinstance(e, basestring):
        msg = '%s: %s' % (step, e)
        logger.error(step)
    else:
        logger.error(step)
        logger.exception(e)
    # remove login, password from error before return as json data
    error = fixError(e)
    if raiseError:
        raise m01.remote.exceptions.JobError(error)
    return {'status': False, 'steps': steps, 'error': error}


def logStep(steps, step, msg):
    logger.info('%s: %s' % (step, msg))
    steps.append({'step': step, 'msg': msg})


# package manager
class PackageManager(object):
    """Scrapy package manager"""

    zope.interface.implements(interfaces.IPackageManager)
    zope.component.adapts(interfaces.IScrapyRoot)

    def __init__(self, context):
        """initialize package installer"""
        self.context = context

    @property
    def pkgsDir(self):
        return self.context.pkgsDir

    @property
    def pypiURL(self):
        return self.context.pypiURL

    def doAddPackage(self, pkgName, pkgVersion, pyVersion, md5Digest=None,
        testing=True, raiseError=True):
        """Add a package to the given location using setuptools.

        This method uses a setuptools and buildout for install a package.

        Use the following authentication pattern if you need authentication:
        http://username:password@domain/pypi/pkg/version/file#checksum

        """
        # setup base name
        baseName = '%s-%s' % (pkgName, pkgVersion)
        # setup response values
        spiderNames = {}
        steps = []

        # define locations
        pkgDir = os.path.join(self.pkgsDir, pkgName, pkgVersion, pyVersion)
        binDir = os.path.join(pkgDir, 'bin')

        # first check if we already have the package and the pkgDir is not empty
        if os.path.exists(pkgDir) and os.listdir(pkgDir):
            # we already have a version of that package, abort
            msg = 'Duplicated Package found at: %s' % pkgDir
            return logError(steps, 'duplication', msg, raiseError)

        # find package urls with our pypi proxy
        try:
            logStep(steps, 'fetch', {'pypiURL': self.pypiURL,
                                     'pkgName': pkgName,
                                     'pkgVersion': pkgVersion})
            urls = pypi.fetchPackageReleaseURLs(self.pypiURL, pkgName,
                pkgVersion)
        except Exception, e:
            return logError(steps, 'fetch data', e, raiseError)

        # find download URL based on known formats
        # NOTE: binare distributions (.egg) are not allowed!
        pkgURL = None
        fName = None
        fDigest = None
        for data in urls:
            fn = data['filename']
            for ext in ['zip', 'tgz', 'tar.gz', 'tar.bz2']:
                if fn == '%s.%s' % (baseName, ext):
                    fName = fn
                    fDigest = data['md5_digest']
                    pkgURL = data['url']
                    break

        if pkgURL is None:
            msg = 'Package download url not found in: %s' % ', '.join(urls)
            return logError(steps, 'fetch url', msg, raiseError)

        # check md5 checksum based on meta data 
        if md5Digest and fDigest:
            logStep(steps, 'fetch md5_digest', 'validate')
            if md5Digest != fDigest:
                msg = "MD5 sum does not match: %s / %s for release data %s" % (
                        md5Digest, fDigest, pkgURL)
                return logError(steps, 'fetch md5_digest', msg, raiseError)
            else:
                logStep(steps, 'fetch md5_digest', 'OK')

        # download package including md5Digest data validation
        try:
            logStep(steps, 'download', pkgURL)
            pkgData = downloadPackage(pkgURL, md5Digest)
        except DownloadError, e:
            return logError(steps, 'download', e, raiseError)

        # write to a tmp directory before we unpack
        tmpDir = tempfile.mkdtemp('scrapyd')
        tmpPath =   os.path.join(tmpDir, fName)
        logStep(steps, 'unpack', pkgDir)
        try:
            # store the package data to tmp file
            f = open(tmpPath, 'wb')
            f.write(pkgData)
            f.close()

            # unpack the package to the pkgs directory
            try:
                logStep(steps, 'unpack', tmpDir)
                unpackPackage(tmpPath, tmpDir)
            except setuptools.archive_util.UnrecognizedFormat, e:
                return logError(steps, 'unpack unrecognized', e, raiseError)

            # find top level and copy to pkgs folder
            logStep(steps, 'unpack move', pkgDir)
            movePackage(tmpDir, pkgDir)
        except Exception, e:
            # remove tmp dir
            rmtree(tmpDir)
            return logError(steps, 'unpack move', e, raiseError)
        finally:
            # remove tmp dir
            rmtree(tmpDir)

        # get python executable based on product config stored in scrapy root
        py = self.context.pythonVersions.get(pyVersion)
        if py is not None:
            # our python comes from the pythonVersions settings, check the path
            if not os.path.exists(py):
                msg = 'Python not found at: %s, check pythonversions config' % py
                return logError(steps, 'bootstrap', msg, raiseError)
        else:
            py =  'python'

        # run bootstrap
        cmd = '%s bootstrap.py -c worker.cfg' % py
        stdout, stderr, code = doCommand(cmd, cwd=pkgDir)
        logStep(steps, 'bootstrap', stdout.strip())
        if code:
            rmtree(pkgDir)
            return logError(steps, 'bootstrap', stderr, raiseError)

        # run buildout script
        if is_win32:
            fn = 'buildout.exe'
        else:
            fn = 'buildout'
        cmd = buildCommand(binDir, fn, '-c worker.cfg')
        stdout, stderr, code = doCommand(cmd, cwd=pkgDir)
        logStep(steps, 'buildout', stdout)
        if code:
            rmtree(pkgDir)
            return logError(steps, 'buildout', stderr, raiseError)

        if testing:
            # run test script if required
            if is_win32:
                # XXX, should we use "test --exit-with-status -1"
                fn = 'test.exe'
            else:
                fn = 'test'
            cmd = buildCommand(binDir, fn)
            stdout, stderr, code = doCommand(cmd, cwd=pkgDir)
            logStep(steps, 'test', stdout)
            if code:
                rmtree(pkgDir)
                return logError(steps, 'test', stderr, raiseError)

        # list spiders from installed package
        logStep(steps, 'list', pkgDir)
        error = None
        try:
            spiderNames, error, code = listSpiders(pkgDir)
        except Exception, e:
            rmtree(pkgDir)
            error = e
        if error:
            rmtree(pkgDir)
            return logError(steps, 'list', error, raiseError)

        # ensure ScrapyPackage in mongodb
        msg = '%s %s' % (pkgName, pkgVersion)
        logStep(steps, 'ensureScrapyPackage', msg)
        try:
            self.context.doEnsureScrapyPackage(pkgName, pkgVersion, pyVersion,
                md5Digest, spiderNames)
        except Exception, e:
            rmtree(pkgDir)
            return logError(steps, 'doEnsureScrapyPackage', e, raiseError)

        # retrun status
        return {'status': True, 'spiders': spiderNames, 'error': None,
                'steps': steps}

    def doRemovePackage(self, pkgName, pkgVersion, pyVersion):
        """Remove a package installed with package installer"""
        steps = []

        # check if the package exists
        pkgDir = os.path.join(self.pkgsDir, pkgName, pkgVersion, pyVersion)

        logStep(steps, 'exists', pkgDir)
        if not os.path.exists(pkgDir):
            msg = 'Package not installed'
            return logError(steps, 'exists', msg)

        # remove package
        logStep(steps, 'rmtree', pkgDir)
        try:
            rmtree(pkgDir)
        except OSError, e:
            return logError(steps, 'rmtree', e)

        # ensure ensureScrapyPackage in mognodb
        msg = '%s %s %s' % (pkgName, pkgVersion, pyVersion)
        logStep(steps, 'doRemoveScrapyPackage', msg)
        try:
            self.context.doRemoveScrapyPackage(pkgName, pkgVersion, pyVersion)
        except Exception, e:
            return logError(steps, 'doRemoveScrapyPackage', e)

        # retrun status
        return {'status': True, 'error': None, 'steps': steps}

    def listAllSpiders(self):
        """Returns a list of spiders from all installed packages"""
        return listAllSpiders(self.pkgsDir)

    def listSpiders(self, pkgName, pkgVersion, pyVersion):
        """Retruns a list of spiders"""
        pkgDir = os.path.join(self.pkgsDir, pkgName, pkgVersion, pyVersion)
        spiders, stderr, code = listSpiders(pkgDir)
        return {'spiders': spiders, 'error': stderr and stderr or None,
                'code': code}

    def doRunSpider(self, pkgName, pkgVersion, pyVersion, spiderName,
        cmdOptions=None, raiseError=True):
        """Start a specific spider from a given package and version"""
        pkgDir = os.path.join(self.pkgsDir, pkgName, pkgVersion, pyVersion)
        stdout, stderr, code = runSpider(pkgDir, spiderName, cmdOptions)
        # our subprocess returns every ERROR as stderr but doesn't set a correct
        # returncode.
        # see s01.scrapy.comdline and s01.scrapy.log for more info
        if code and raiseError:
            raise m01.remote.exceptions.JobError(stderr)
        elif stderr:
            status = False
        else:
            status = True
        return {'status': status, 'error': stderr, 'code': code}
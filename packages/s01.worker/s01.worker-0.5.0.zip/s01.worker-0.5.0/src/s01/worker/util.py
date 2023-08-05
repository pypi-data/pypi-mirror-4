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

import os
import os.path
import subprocess

import s01.core.util


# configuration
def getPackageDirectory():
    """Returns the package directory where scrapy spiders get installed"""
    confKey = 'package_dir'
    envKey = 'S01_WORKER_PACKAGE_DIRECTORY'
    path = s01.core.util.getConfig('s01.worker', confKey, envKey)
    if not path:
        raise ValueError("Missing package_dir in buildout.cfg")
    elif not os.path.exists(path):
        raise ValueError("given package_dir path '%s' does not exist" % path)
    return os.path.abspath(path)

pkgsDir = getPackageDirectory()


def getPYPIURL():
    """Returns the package directory where scrapy spiders get installed"""
    confKey = 'pypi_url'
    envKey = 'S01_WORKER_PYPI_URL'
    url = s01.core.util.getConfig('s01.worker', confKey, envKey)
    if not url:
        raise ValueError("Missing pypi_url in buildout.cfg")
    return str(url)

pypiURL = getPYPIURL()


def getServerName():
    """Returns the server name. Not this name must be unique not other server
    should use the same name if you run more then one server.
    """
    confKey = 'server_name'
    envKey = 'S01_WORKER_SERVER_NAME'
    url = s01.core.util.getConfig('s01.worker', confKey, envKey)
    if not url:
        raise ValueError("Missing server_name in buildout.cfg")
    return url

serverName = getServerName()


# set major python version, use pythonversions if you need the full version.
def getShellPythonVersion():
    """Get the correct shell python version not the version from our process"""
    cmd = ["python", "-c",
           "import sys; v = sys.version_info; print '%i.%i' % (v[0], v[1])"]
    stdout = stderr = subprocess.PIPE
    p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, shell=True)
    stdout, stderr = p.communicate()
    if p.returncode:
        raise ValueError("Default python not found on system") 
    return unicode(stdout.strip())

defaultPythonVersion = getShellPythonVersion()


# set job worker options
try:
    value = s01.core.util.getConfig('s01.worker', 'threads',
        'S01_WORKER_THREADS')
    jobWorkerMaxThreads = int(value)
except ValueError:
    jobWorkerMaxThreads = 1


try:
    t = s01.core.util.getConfig('s01.worker',
        'wait_time', 'S01_WORKER_WAIT_TIME')
    jobWorkerWaitTime = float(t)
except ValueError:
    jobWorkerWaitTime = 1.0


# set error log option
try:
    conf = s01.core.util.getConfig('s01.worker',
        'copy_to_zlog', 'S01_WORKER_COPY_TO_ZLOG')
    copy_to_zlog = s01.core.util.asBool(conf)
except ValueError:
    copy_to_zlog = False


# set auto start option
try:
    auto = s01.core.util.getConfig('s01.worker', 'auto_start_processor',
        'S01_WORKER_AUTO_START_RPOCESSOR')
    autoStartProcessor = s01.core.util.asBool(auto)
except ValueError:
    autoStartProcessor = False

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
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='s01.worker',
    version='0.5.0',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "Scrapy worker based on buildout with JSON-RPC 2.0 API",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "scrapy s01 p01 mongodb buildout json-rpc zope zope3",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/s01.worker',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['s01'],
    extras_require=dict(
        test=[
            'zope.testing',
            'm01.mongo [test]',
            's01.client',
             ]),
    install_requires = [
        'setuptools',
        'ZConfig',
        'transaction',
        'm01.mongo',
        'm01.remote',
        's01.core',
        'p01.recipe.setup [paste]',
        'p01.recipe.setup',
        'z3c.jsonrpc',
        'zope.app.appsetup',
        'zope.app.publication',
        'zope.authentication',
        'zope.browserpage',
        'zope.component',
        'zope.event',
        'zope.interface',
        'zope.location',
        'zope.principalregistry',
        'zope.publisher',
        'zope.security',
        'zope.securitypolicy',
        'zope.site',
        ],
    zip_safe = False,
    entry_points = """
        [paste.app_factory]
        app = s01.worker.wsgi:application_factory
        """,
)
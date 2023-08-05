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
"""WSGI factory
$Id:$
"""
__docformat__ = "reStructuredText"

import logging
import os
import os.path
import sys
import ZConfig
import transaction

import zope.component
import zope.app.appsetup.product
import zope.app.appsetup.appsetup

from s01.worker import interfaces
from s01.worker import publisher


def config(configfile, schemafile, features=()):
    conf = {}
    # load the configuration schema file
    schema = ZConfig.loadSchema(schemafile)

    # load the configuration file
    try:
        options, handlers = ZConfig.loadConfig(schema, configfile)
    except ZConfig.ConfigurationError, msg:
        sys.stderr.write("Error: %s\n" % str(msg))
        sys.exit(2)

    # get python versions, see zope.conf and s01/worker/schema/schema.xml
    vKey = 'python_versions_%s' % sys.platform
    attrs  = options.getSectionAttributes()
    if vKey in attrs:
        conf['pythonversions'] = options.__dict__.get(vKey)

    # insert all specified Python paths
    if options.path:
        sys.path[:0] = [os.path.abspath(p) for p in options.path]

    # parse product configs
    zope.app.appsetup.product.setProductConfigurations(options.product_config)

    # setup the event log
    options.eventlog()

    # insert the devmode feature, if turned on
    if options.devmode:
        features += ('devmode',)
        logging.warning("Developer mode is enabled: this is a security risk "
            "and should NOT be enabled on production servers. Developer mode "
            "can usually be turned off by setting the `devmode` option to "
            "`off` or by removing it from the instance configuration file "
            "completely.")

    # execute the ZCML configuration.
    zope.app.appsetup.appsetup.config(options.site_definition,
        features=features)

    return conf


def getWSGIApplication(configfile, schemafile=None, debug=False, features=(),
                       requestFactory=publisher.PublicationRequestFactory,
                       handle_errors=True):
    # config based on paste.conf which includes paste.zcml
    conf = config(configfile, schemafile, features)
    app = zope.component.getUtility(interfaces.IScrapyRoot)
    # set python path for given versions
    if 'pythonversions' in conf:
        pythonVersions = conf['pythonversions']
        # check python version path
        data = {}
        for v, path in pythonVersions.items():
            if not os.path.exists(path):
                logging.warn("Python executable at '%s' is missing" % path)
            data[unicode(v)] = unicode(path)
        app.pythonVersions = data
    # find mongodb and say hello
    # we can't load mongo before we applied the product config
    import s01.core.mongo
    pool = s01.core.mongo.mongoConnectionPool
    try:
        con = pool.connection
        logging.info("Connected to mongodb on %s:%s" % (con.host, con.port))
        # now if mongo is available, ensure jobFactories
        msgs, commitRequired = app.ensureJobFactories()
        for msg in msgs:
            logging.info(msg)
        # commit jobFactory adding transaction  if required
        if commitRequired:
            transaction.commit()

    except Exception, e: # we will never fail
        msg = "NOT connected to mongodb at %s:%s" % (pool.host, pool.port)
        logging.warn(msg)
        print msg
    if debug:
        return publisher.PMDBWSGIPublisherApplication(app, requestFactory,
            handle_errors)
    else:
        return publisher.WSGIPublisherApplication(app, requestFactory,
            handle_errors)


# prevent to import from util because we first need to setup product config
def asBool(obj):
    if isinstance(obj, basestring):
        obj = obj.lower()
        if obj in ('1', 'true', 'yes', 't', 'y'):
            return True
        if obj in ('0', 'false', 'no', 'f', 'n'):
            return False
    return bool(obj)


def application_factory(global_conf, *args, **local_conf):
    debug = asBool(local_conf.get('debug', False))
    configfile = os.path.join(global_conf['here'], 'zope.conf')
    schemafile = os.path.join(os.path.dirname(__file__), 'schema', 'schema.xml')
    global APPLICATION
    APPLICATION = getWSGIApplication(configfile, schemafile, debug)
    return APPLICATION

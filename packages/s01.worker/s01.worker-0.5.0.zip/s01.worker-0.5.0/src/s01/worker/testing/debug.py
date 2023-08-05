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

import base64, time
import urllib
from StringIO import StringIO

import zope.component
from zope.publisher.browser import setDefaultSkin
from zope.app.appsetup import config

from s01.worker.publisher import ScrapyPublication
from s01.worker.publish import publish as _publish, debug_call
from s01.worker import interfaces


class Debugger(object):

    root = None

    def __init__(self, config_file=None):
        if config_file is not None:
            config(config_file)
        self.root = zope.component.getUtility(interfaces.IScrapyRoot)

    def _request(self,
                 path='/', stdin='', basic=None,
                 environment = None, form=None,
                 request=None, publication=ScrapyPublication):
        """Create a request"""

        env = {}

        if type(stdin) is str:
            stdin = StringIO(stdin)

        p=path.split('?')
        if len(p)==1:
            env['PATH_INFO'] = p[0]
        elif len(p)==2:
            env['PATH_INFO'], env['QUERY_STRING'] = p
        else:
            raise ValueError("Too many ?s in path", path)

        env['PATH_INFO'] = urllib.unquote(env['PATH_INFO'])

        if environment is not None:
            env.update(environment)

        if basic:
            env['HTTP_AUTHORIZATION']="Basic %s" % base64.encodestring(basic)

        pub = publication(self.root)

        if request is not None:
            request = request(stdin, env)
        else:
            # avoid recursiv import
            from p01.scrapy.testing import ScrapyTestRequest
            request = ScrapyTestRequest(stdin, env)
            setDefaultSkin(request)
        request.setPublication(pub)
        if form:
            # This requires that request class has an attribute 'form'
            # (ScrapyRequest has, TestRequest hasn't)
            request.form.update(form)

        return request

    def publish(self, path='/', stdin='', *args, **kw):
        t, c = time.time(), time.clock()
        request = self._request(path, stdin, *args, **kw)
        # agroszer: 2008.feb.1.: if a retry occurs in the publisher,
        # the response will be LOST, so we must accept the returned request
        request = _publish(request)
        getStatus = getattr(request.response, 'getStatus', lambda: None)
        headers = request.response.getHeaders()
        headers.sort()
        print 'Status %s\r\n%s\r\n\r\n%s' % (
            request.response.getStatusString(),
            '\r\n'.join([("%s: %s" % h) for h in headers]),
            request.response.consumeBody(),
            )
        return time.time()-t, time.clock()-c, getStatus()

    def run(self, *args, **kw):
        t, c = time.time(), time.clock()
        request = self._request(*args, **kw)
        # agroszer: 2008.feb.1.: if a retry occurs in the publisher,
        # the response will be LOST, so we must accept the returned request
        request = _publish(request, handle_errors=False)
        getStatus = getattr(request.response, 'getStatus', lambda: None)

        return time.time()-t, time.clock()-c, getStatus()

    def debug(self, *args, **kw):

        import pdb

        class Pdb(pdb.Pdb):
            def do_pub(self,arg):
                if hasattr(self,'done_pub'):
                    print 'pub already done.'
                else:
                    self.do_s('')
                    self.do_s('')
                    self.do_c('')
                    self.done_pub=1
            def do_ob(self,arg):
                if hasattr(self,'done_ob'):
                    print 'ob already done.'
                else:
                    self.do_pub('')
                    self.do_c('')
                    self.done_ob=1

        db=Pdb()

        request = self._request(*args, **kw)
        fbreak(db, _publish)
        fbreak(db, debug_call)

        print '* Type c<cr> to jump to published object call.'
        db.runcall(_publish, request)


def fbreak(db, meth):
    try:
        meth = meth.im_func
    except AttributeError:
        pass
    code = meth.func_code
    lineno = getlineno(code)
    filename = code.co_filename
    db.set_break(filename,lineno)



try:
    from codehack import getlineno
except:
    def getlineno(code):
        return code.co_firstlineno

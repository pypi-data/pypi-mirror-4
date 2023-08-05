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

import transaction

import zope.component
import zope.interface
import zope.event
import zope.security.management
from zope.site import hooks
from zope.security.checker import ProxyFactory
from zope.principalregistry.principalregistry import principalRegistry
from zope.authentication.interfaces import IFallbackUnauthenticatedPrincipal
from zope.app.publication.interfaces import BeforeTraverseEvent
from zope.app.publication.interfaces import IRequestPublicationFactory
from zope.app.publication.interfaces import IPublicationRequestFactory
from zope.app.publication.httpfactory import chooseClasses
from zope.publisher.interfaces import ISkinnable
from zope.publisher.skinnable import setDefaultSkin
from zope.publisher.interfaces import logginginfo

import z3c.jsonrpc.publication
import z3c.jsonrpc.publisher

from s01.worker import interfaces
from s01.worker.publish import publish


class ScrapyRequest(z3c.jsonrpc.publisher.JSONRPCRequest):
    """Scrapy request mixin class using the scprayd as applictaion.
    
    Note: we need to define __slots__ if you like to expose the _app
    in your request mixin class.
    """

    zope.interface.implements(interfaces.IScrapyRequest)

    __slots__ = (
        '_root',
        )

    root = property(lambda self: self._root)

    def setPublication(self, pub):
        self._root = pub.root
        super(ScrapyRequest, self).setPublication(pub)


class ScrapyPublication(z3c.jsonrpc.publication.JSONRPCPublication):
    """Scrapy publication class"""

    zope.interface.implements(interfaces.IScrapyPublication)

    def __init__(self, root):
        """initialize publication with given application.
        
        Take care, this instance is cached as a singleton in 
        IPublicationRequestFactory
        """
        self.root = root

    def startRequest(self, request):
        """Start new interaction and beginn transaction.
        
        This new hook allows us to prepare everything and handle
        request.processInputs with transaction control.
        """
        # set site hook
        hooks.setSite(self.root)
        # start transaction
        transaction.begin()

    def beforeTraversal(self, request):
        """Authenticate and set principal

        Note, we allready started the transaction and interaction.
        """
        # authenticate after we called processInputs
        lpw = request._authUserPW()
        if lpw is None:
            principal = self.unauthenticatedPrincipal()
            if principal is None:
                # Get the fallback unauthenticated principal
                principal = zope.component.getUtility(
                    IFallbackUnauthenticatedPrincipal)
        else:
            login, password = lpw
            try:
                principal = principalRegistry.getPrincipalByLogin(login)
                if not principal.validate(password):
                    principal = None
            except (KeyError, AttributeError), e:
                principal = None

        # set principal
        request.setPrincipal(principal)
        # start new interaction
        zope.security.management.newInteraction(request)

    def callTraversalHooks(self, request, ob):
        # notify before traverse event. There is no need for authenticate
        zope.event.notify(BeforeTraverseEvent(ob, request))

    def afterTraversal(self, request, ob):
        # there is no need for authenticate after traversal like the zope
        # publication implementation does
        raise NotImplementedError("Our publish method does not use this method")

    def getApplication(self, request):
        """Returns the zope applicaton (root)."""
        return ProxyFactory(self.root)

    def _maybePlacefullyAuthenticate(self, request, ob):
        # there is no need for another authenticate call since we only use
        # the global authentication
        raise NotImplementedError("Our publish method does not use this method")


class ScrapyJSONRPCFactory(object):
    """Scrapy request publication factory which returns the right publication"""

    zope.interface.implements(IRequestPublicationFactory)
    
    def canHandle(self, environment):
        return True
        
    def __call__(self):
        return ScrapyRequest, ScrapyPublication


class PublicationRequestFactory(object):
    """Publication request factory which knows application instead of database.
    """
    zope.interface.implements(IPublicationRequestFactory)

    def __init__(self, root):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        self._root = root
        self._publication_cache = {}

    def __call__(self, input_stream, env):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        method = env.get('REQUEST_METHOD', 'GET').upper()
        request_class, publication_class = chooseClasses(method, env)

        publication = self._publication_cache.get(publication_class)
        if publication is None:
            publication = publication_class(self._root)
            self._publication_cache[publication_class] = publication

        request = request_class(input_stream, env)
        request.setPublication(publication)
        if ISkinnable.providedBy(request):
            # only ISkinnable requests have skins
            setDefaultSkin(request)
        return request


class WSGIPublisherApplication(object):
    """A WSGI application implementation for the zope publisher

    Instances of this class can be used as a WSGI application object.

    The class relies on a properly initialized request factory.
    """
    zope.interface.implements(interfaces.IWSGIApplication)

    def __init__(self, root, factory=PublicationRequestFactory,
                 handleErrors=True):
        self.root = root
        self.requestFactory = factory(root)
        self.handleErrors = handleErrors

    def __call__(self, environ, start_response):
        """See zope.app.wsgi.interfaces.IWSGIApplication"""
        request = self.requestFactory(environ['wsgi.input'], environ)

        # Let's support post-mortem debugging
        handle_errors = environ.get('wsgi.handleErrors', self.handleErrors)

        request = publish(request, handle_errors=handle_errors)
        response = request.response

        # Get logging info from principal for log use
        logging_info = logginginfo.ILoggingInfo(request.principal, None)
        if logging_info is None:
            message = '-'
        else:
            message = logging_info.getLogMessage()
        environ['wsgi.logging_info'] = message

        # Start the WSGI server response
        start_response(response.getStatusString(), response.getHeaders())

        # Return the result body iterable.
        return response.consumeBodyIter()


class PMDBWSGIPublisherApplication(WSGIPublisherApplication):
    """Post Mortem Debugger Publisher application"""

    def __call__(self, environ, start_response):
        environ['wsgi.handleErrors'] = self.handleErrors

        # Call the application to handle the request and write a response
        try:
            wsgiApp = super(PMDBWSGIPublisherApplication, self)
            return wsgiApp.__call__(environ, start_response)
        except Exception, error:
            import sys
            import pdb
            print "%s:" % sys.exc_info()[0]
            print sys.exc_info()[1]
            try:
                pdb.post_mortem(sys.exc_info()[2])
                raise
            finally:
                pass










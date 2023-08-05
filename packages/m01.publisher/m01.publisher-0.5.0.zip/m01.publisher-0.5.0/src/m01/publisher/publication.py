##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import transaction

import zope.component
import zope.event
import zope.security.management
from zope.site import hooks
from zope.authentication.interfaces import IAuthentication
from zope.security.checker import ProxyFactory
from zope.authentication.interfaces import IFallbackUnauthenticatedPrincipal
from zope.app.publication.interfaces import BeforeTraverseEvent
from zope.app.publication.interfaces import IRequestPublicationFactory
from zope.app.publication.interfaces import IBrowserRequestFactory

import zope.app.publication.browser
import z3c.jsonrpc.publication

from m01.publisher import interfaces
from m01.publisher import publisher


class PublicationMixin(object):
    """Publication mixin class for ZODB less publications.
    
    Note, you should implement your own publication class and use them in a 
    publication factory. After that, you can register your own publication
    factory or you can use the BrowserPublication and
    BrowserFactory defined below.
    """

    def __init__(self, app):
        """initialize publication with given application.
        
        Take care, this instance is cached as a singleton in 
        IPublicationRequestFactory
        """
        # avoid super call which whould setup self.db
        self.app = app

    def startRequest(self, request):
        """Start new interaction and beginn transaction.
        
        This new hook allows us to prepare everything and handle
        request.processInputs with transaction control.
        """
        # set site hook
        hooks.setSite(self.app)
        # start transaction
        transaction.begin()

    @property
    def _auth(self):
        """Knows how to get the IAuthentication utility."""
        sm = self.app.getSiteManager()
        return sm.queryUtility(IAuthentication)

    def beforeTraversal(self, request):
        """Authenticate and set principal

        Note, we allready started the transaction and interaction.
        """
        # authenticate after we called processInputs
        auth = self._auth
        principal = auth.authenticate(request)
        if principal is None:
            principal = auth.unauthenticatedPrincipal()
            if principal is None:
                # Get the fallback unauthenticated principal
                principal = zope.component.getUtility(
                    IFallbackUnauthenticatedPrincipal)

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
        return ProxyFactory(self.app)

    def _maybePlacefullyAuthenticate(self, request, ob):
        # there is no need for another authenticate call since we only use one
        # global authentication
        raise NotImplementedError("Our publish method does not use this method")


# browser
class BrowserPublication(PublicationMixin,
    zope.app.publication.browser.BrowserPublication):
    """Browser publication
    
    The BrowserPublication which inherits ZopePublication will start the
    transaction in the beforeTraversal method. See startRequest for more info.

    """

    zope.interface.implements(interfaces.IBrowserPublication)


class BrowserFactory(object):
    """Browser request factory which returns the right publication"""

    zope.interface.implements(IRequestPublicationFactory)

    def canHandle(self, environment):
        return True

    def __call__(self):
        # hook wihich allows to register a custom IBrowserRequestFactory
        request_class = zope.component.queryUtility(IBrowserRequestFactory,
                default=publisher.BrowserRequest)
        return request_class, BrowserPublication


# json-rpc
class JSONRPCPublication(PublicationMixin,
    z3c.jsonrpc.publication.JSONRPCPublication):
    """JSON-RPC publication class"""

    zope.interface.implements(interfaces.IJSONRPCPublication)



class JSONRPCFactory(object):
    """JSON-RPC request factory which returns the right publication"""

    zope.interface.implements(IRequestPublicationFactory)

    def canHandle(self, environment):
        return True

    def __call__(self):
        # hook wihich allows to register a custom IBrowserRequestFactory
        request_class = zope.component.queryUtility(IBrowserRequestFactory,
                default=publisher.JSONRPCRequest)
        return request_class, JSONRPCPublication

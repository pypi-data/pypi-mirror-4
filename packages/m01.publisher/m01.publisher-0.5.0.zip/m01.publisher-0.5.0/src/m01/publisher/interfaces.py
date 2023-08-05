##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
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

import zope.interface
import zope.component.interfaces
import zope.location.interfaces
import zope.publisher.interfaces.browser
import z3c.jsonrpc.interfaces


class IWSGIApplication(zope.interface.Interface):
    """A WSGI application."""

    def __call__(environ, start_response):
        """Called by a WSGI server.

        The ``environ`` parameter is a dictionary object, containing CGI-style
        environment variables. This object must be a builtin Python dictionary
        (not a subclass, UserDict or other dictionary emulation), and the
        application is allowed to modify the dictionary in any way it
        desires. The dictionary must also include certain WSGI-required
        variables (described in a later section), and may also include
        server-specific extension variables, named according to a convention
        that will be described below.

        The ``start_response`` parameter is a callable accepting two required
        positional arguments, and one optional argument. For the sake of
        illustration, we have named these arguments ``status``,
        ``response_headers``, and ``exc_info``, but they are not required to
        have these names, and the application must invoke the
        ``start_response`` callable using positional arguments
        (e.g. ``start_response(status, response_headers)``).
        """


class IApplication(zope.location.interfaces.IRoot,
    zope.component.interfaces.ISite, zope.location.interfaces.ILocation):
    """Non ZODB application root does not provide IContainer."""


class IRequestMixin(zope.interface.Interface):
    """Request mixin class."""

    app = zope.interface.Attribute("""Application (root) object""")
    appURL = zope.interface.Attribute("""Application (root) URL""")


class IBrowserRequest(zope.publisher.interfaces.browser.IBrowserRequest,
    IRequestMixin):
    """Browser request."""


class IJSONRPCRequest(z3c.jsonrpc.interfaces.IJSONRPCRequest, IRequestMixin):
    """JSON-RPC request."""


class IPublicationMixin(zope.interface.Interface):
    """Publication mixin class"""

    def startRequest(self, request):
        """Start new interaction and beginn transaction.
        
        This new hook allows us to prepare everything and handle
        request.processInputs with transaction control.
        """


class IBrowserPublication(zope.publisher.interfaces.browser.IBrowserPublication,
    IPublicationMixin):
    """Bowser publication."""


class IJSONRPCPublication(z3c.jsonrpc.interfaces.IJSONRPCPublication,
    IPublicationMixin):
    """JSON-RPC publication."""


# events
class IApplicationCreatedEvent(zope.component.interfaces.IObjectEvent):
    
    app = zope.interface.Attribute(u"Published Application")


class ApplicationCreatedEvent(object):
    
    zope.interface.implements(IApplicationCreatedEvent)
    
    def __init__(self, application):
        self.object = application

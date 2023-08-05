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

import os
import sys
import logging
import ZConfig
import zope.component
import zope.interface
import zope.event
import zope.app.appsetup.product
from zope.publisher.interfaces.logginginfo import ILoggingInfo
from zope.publisher.interfaces import ISkinnable
from zope.publisher.skinnable import setDefaultSkin
from zope.app.appsetup import appsetup
from zope.app.publication.interfaces import IPublicationRequestFactory
from zope.app.publication.httpfactory import chooseClasses


from m01.publisher import interfaces
from m01.publisher.publish import publish


class PublicationRequestFactory(object):
    """Publication request factory which knows application instead of database.
    """
    zope.interface.implements(IPublicationRequestFactory)

    def __init__(self, app):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        self._app = app
        self._publication_cache = {}

    def __call__(self, input_stream, env):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        method = env.get('REQUEST_METHOD', 'GET').upper()
        request_class, publication_class = chooseClasses(method, env)

        publication = self._publication_cache.get(publication_class)
        if publication is None:
            publication = publication_class(self._app)
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

    def __init__(self, app, factory=PublicationRequestFactory,
                 handleErrors=True):
        self.app = app
        self.requestFactory = factory(app)
        self.handleErrors = handleErrors

    def __call__(self, environ, start_response):
        """See zope.app.wsgi.interfaces.IWSGIApplication"""
        request = self.requestFactory(environ['wsgi.input'], environ)

        # Let's support post-mortem debugging
        handle_errors = environ.get('wsgi.handleErrors', self.handleErrors)

        request = publish(request, handle_errors=handle_errors)
        response = request.response

        # Get logging info from principal for log use
        logging_info = ILoggingInfo(request.principal, None)
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

    def __call__(self, environ, start_response):
        environ['wsgi.handleErrors'] = False

        # Call the application to handle the request and write a response
        try:
            app =  super(PMDBWSGIPublisherApplication, self)
            return app.__call__(environ, start_response)
        except Exception, error:
            import sys, pdb
            print "%s:" % sys.exc_info()[0]
            print sys.exc_info()[1]
            #import zope.security.management
            #zope.security.management.restoreInteraction()
            try:
                pdb.post_mortem(sys.exc_info()[2])
                raise
            finally:
                pass #zope.security.management.endInteraction()


def config(configfile, schemafile, features=()):
    # load the configuration schema file
    schema = ZConfig.loadSchema(schemafile)

    # load the configuration file
    try:
        options, handlers = ZConfig.loadConfig(schema, configfile)
    except ZConfig.ConfigurationError, msg:
        sys.stderr.write("Error: %s\n" % str(msg))
        sys.exit(2)

    # insert all specified Python paths
    if options.path:
        sys.path[:0] = [os.path.abspath(p) for p in options.path]

    # parse product configs
    zope.app.appsetup.product.setProductConfigurations(
        options.product_config)

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
    appsetup.config(options.site_definition, features=features)


def getWSGIApplication(configfile, schemafile=None, features=(),
                       requestFactory=PublicationRequestFactory,
                       handle_errors=True):
    # config based on paste.conf which included paste.zcml
    config(configfile, schemafile, features)
    app = zope.component.getUtility(interfaces.IApplication)

    wsgi = WSGIPublisherApplication(app, requestFactory, handle_errors)

    # create the application, notify subscribers.
    zope.event.notify(interfaces.ApplicationCreatedEvent(app))

    return wsgi


def application_factory(global_conf, zope_conf=None, **local_conf):
    if zope_conf is not None:
        # You can simply define a zope_conf argument in your
        # paste.ini file app section like:
        # [app:zope]
        # use = egg:m01.publisher#app
        # zope_conf = app-zope.conf
        configfile = os.path.join(global_conf['here'], zope_conf)
    else:
        # this part works with p01.recipe.setup:paste which uses the following
        # name convention for generate the script:
        # <part-name>-paste.ini 
        # <part-name>-zope.conf 
        # <part-name>-site.zcml
        # extract part name given from buildout recipe
        pasteName = os.path.basename(global_conf['__file__'])
        confName = '%szope.conf' % pasteName[:-len('paste.ini')]
        confPath = os.path.join(global_conf['here'], confName)
        if os.path.isfile(confPath):
            configfile = confPath
        else:
            # try default zope.conf as zope_conf name
            confPath = os.path.join(global_conf['here'], 'zope.conf')
            if os.path.isfile(confPath):
                configfile = confPath
            else:
                raise ValueError(
                    "Can't find paster zope.conf file for m01.publisher.wsgi")
    schemafile = os.path.join(os.path.dirname(__file__), 'schema', 'schema.xml')
    global APPLICATION
    APPLICATION = getWSGIApplication(configfile, schemafile)
    return APPLICATION

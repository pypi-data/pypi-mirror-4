###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: __init__.py 737 2007-11-18 22:24:11Z roger.ineichen $
"""


import copy
import httplib
import logging
import mechanize
import os.path
import re
import rfc822
import socket
import sys
import unittest
import doctest
from Cookie import SimpleCookie
from cStringIO import StringIO

import transaction

import zope.component
from zope.component import hooks
from zope.publisher.interfaces import ISkinnable
from zope.publisher.browser import BrowserLanguages
from zope.publisher.skinnable import setDefaultSkin

import zope.testbrowser.browser

import zope.app.appsetup.product
from zope.app.publication.httpfactory import chooseClasses

import z3c.json.proxy
import z3c.json.transport
from z3c.jsonrpc.publisher import JSON_RPC_VERSION

import m01.publisher.interfaces
import m01.publisher.debug
import m01.publisher.publisher
import m01.publisher.publish


class IManagerSetup(zope.interface.Interface):
    """Utility for enabling up a functional testing manager with needed grants

    TODO This is an interim solution.  It tries to break the dependence
    on a particular security policy, however, we need a much better
    way of managing functional-testing configurations.
    """

    def setUpManager():
        """Set up the manager, zope.mgr
        """


def getRootFolder():
    return zope.component.getUtility(m01.publisher.interfaces.IApplication)


headerre = re.compile(r'(\S+): (.+)$')
def split_header(header):
    return headerre.match(header).group(1, 2)

basicre = re.compile('Basic (.+)?:(.+)?$')
def auth_header(header):
    match = basicre.match(header)
    if match:
        import base64
        u, p = match.group(1, 2)
        if u is None:
            u = ''
        if p is None:
            p = ''
        auth = base64.encodestring('%s:%s' % (u, p))
        return 'Basic %s' % auth[:-1]
    return header


class CookieHandler(object):

    def __init__(self, *args, **kw):
        # Somewhere to store cookies between consecutive requests
        self.cookies = SimpleCookie()
        super(CookieHandler, self).__init__(*args, **kw)

    def httpCookie(self, path):
         """Return self.cookies as an HTTP_COOKIE environment value."""
         l = [m.OutputString().split(';')[0] for m in self.cookies.values()
              if path.startswith(m['path'])]
         return '; '.join(l)

    def loadCookies(self, envstring):
        self.cookies.load(envstring)

    def saveCookies(self, response):
        """Save cookies from the response."""
        # Urgh - need to play with the response's privates to extract
        # cookies that have been set
        # TODO: extend the IHTTPRequest interface to allow access to all
        # cookies
        # TODO: handle cookie expirations
        for k,v in response._cookies.items():
            k = k.encode('utf8')
            self.cookies[k] = v['value'].encode('utf8')
            if v.has_key('path'):
                self.cookies[k]['path'] = v['path']


class TestRequest(m01.publisher.publisher.BrowserRequest):
    """TestRequest which does not apply IDefaultBrowserLayer."""

    def __init__(self, body_instream=None, environ=None, form=None,
                 skin=None, **kw):

        _testEnv =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }

        if environ is not None:
            _testEnv.update(environ)

        if kw:
            _testEnv.update(kw)
        if body_instream is None:
            body_instream = StringIO('')

        super(TestRequest, self).__init__(body_instream, _testEnv)
        if form:
            self.form.update(form)

        # Setup locale object
        langs = BrowserLanguages(self).getPreferredLanguages()
        from zope.i18n.locales import locales
        if not langs or langs[0] == '':
            self._locale = locales.getLocale(None, None, None)
        else:
            parts = (langs[0].split('-') + [None, None])[:3]
            self._locale = locales.getLocale(*parts)

        if skin is not None:
            directlyProvides(self, skin)


class ResponseWrapper(object):
    """A wrapper that adds several introspective methods to a response."""

    def __init__(self, response, path, omit=()):
        self._response = response
        self._path = path
        self.omit = omit
        self._body = None

    def getOutput(self):
        """Returns the full HTTP output (headers + body)"""
        body = self.getBody()
        omit = self.omit
        headers = [x
                   for x in self._response.getHeaders()
                   if x[0].lower() not in omit]
        headers.sort()
        headers = '\n'.join([("%s: %s" % (n, v)) for (n, v) in headers])
        statusline = '%s %s' % (self._response._request['SERVER_PROTOCOL'],
                                self._response.getStatusString())
        if body:
            return '%s\n%s\n\n%s' %(statusline, headers, body)
        else:
            return '%s\n%s\n' % (statusline, headers)

    def getBody(self):
        """Returns the response body"""
        if self._body is None:
            self._body = ''.join(self._response.consumeBody())

        return self._body

    def getPath(self):
        """Returns the path of the request"""
        return self._path

    def __getattr__(self, attr):
        return getattr(self._response, attr)

    __str__ = getOutput


class HTTPCaller(CookieHandler):
    """Execute an HTTP request string via the publisher"""

    def __call__(self, request_string, handle_errors=True, form=None):
        # Commit work done by previous python code.
        transaction.commit()

        # Discard leading white space to make call layout simpler
        request_string = request_string.lstrip()

        # split off and parse the command line
        l = request_string.find('\n')
        command_line = request_string[:l].rstrip()
        request_string = request_string[l+1:]
        method, path, protocol = command_line.split()

        instream = StringIO(request_string)
        environment = {"HTTP_COOKIE": self.httpCookie(path),
                       "HTTP_HOST": 'localhost',
                       "HTTP_REFERER": 'localhost',
                       "REQUEST_METHOD": method,
                       "SERVER_PROTOCOL": protocol,
                       }

        headers = [split_header(header)
                   for header in rfc822.Message(instream).headers]
        for name, value in headers:
            name = ('_'.join(name.upper().split('-')))
            if name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                name = 'HTTP_' + name
            environment[name] = value.rstrip()

        auth_key = 'HTTP_AUTHORIZATION'
        if environment.has_key(auth_key):
            environment[auth_key] = auth_header(environment[auth_key])

        old_site = hooks.getSite()
        hooks.setSite(None)

        request_cls, publication_cls = self.chooseRequestClass(method, path,
                                                               environment)
        debugger = FunctionalTestSetup().getDebugger()
        request = debugger._request(
            path, instream,
            environment=environment,
            request=request_cls, publication=publication_cls)
        if ISkinnable.providedBy(request):
            # only ISkinnable requests have skins
            setDefaultSkin(request)

        if form is not None:
            if request.form:
                raise ValueError("only one set of form values can be provided")
            request.form = form

        request = m01.publisher.publish.publish(request,
            handle_errors=handle_errors)

        response = ResponseWrapper(
            request.response, path,
            omit=('x-content-type-warning', 'x-powered-by'),
            )

        self.saveCookies(response)
        hooks.setSite(old_site)

        return response

    def chooseRequestClass(self, method, path, environment):
        """Choose and return a request class and a publication class"""
        # note that `path` is unused by the default implementation (BBB)
        return chooseClasses(method, environment)


class FunctionalTestSetup(object):
    """Keeps shared state across several functional test cases."""

    __shared_state = { '_init': False }

    def __init__(self, config_file=None, product_config=None):
        """Initializes Zope 3 framework and configuration files."""
        self.__dict__ = self.__shared_state

        if not self._init:

# XXX: skip different test setup
#            # Make sure unit tests are cleaned up
#            zope.app.testing.setup.placefulSetUp()
#            zope.app.testing.setup.placefulTearDown()

            if not config_file:
                config_file = 'ftesting.zcml'
            self.log = StringIO()
            # Make it silent but keep the log available for debugging
            logging.root.addHandler(logging.StreamHandler(self.log))

            self.old_product_config = copy.deepcopy(
                zope.app.appsetup.product.saveConfiguration())
            configs = []
            if product_config:
                configs = zope.app.appsetup.product.loadConfiguration(
                    StringIO(product_config))
                configs = [
                    zope.app.appsetup.product.FauxConfiguration(name, values)
                    for name, values in configs.items()
                    ]
            self.local_product_config = configs
            zope.app.appsetup.product.setProductConfigurations(configs)

            # This handles anything added by generations or other bootstrap
            # subscribers.
            transaction.commit()
            self.debugger = m01.publisher.debug.Debugger(config_file)

            self._config_file = config_file
            self._product_config = product_config
            self._init = True

            # Make a local grant for the test user
            setup = zope.component.queryUtility(IManagerSetup)
            if setup is not None:
                setup.setUpManager()

        elif config_file and config_file != self._config_file:
            # Running different tests with different configurations is not
            # supported at the moment
            raise NotImplementedError('Already configured'
                                      ' with a different config file')

        elif product_config and product_config != self._product_config:
            raise NotImplementedError('Already configured'
                                      ' with different product configuration')

    def setUp(self):
        """Prepares for a functional test case."""
        # Tear down the old demo storages (if any) and create fresh ones
        transaction.abort()
        zope.app.appsetup.product.setProductConfigurations(
            self.local_product_config)

    def tearDown(self):
        """Cleans up after a functional test case."""
        transaction.abort()
        hooks.setSite(None)

    def tearDownCompletely(self):
        """Cleans up the setup done by the constructor."""
        transaction.abort()
# skip tear down since we didn't setup, see above
#        zope.app.testing.setup.placefulTearDown()
        zope.app.appsetup.product.restoreConfiguration(
            self.old_product_config)
        self._config_file = False
        self._product_config = None
        self._init = False

    def getRootFolder(self):
        """Returns the Zope root folder."""
        return getRootFolder()

    def getDebugger(self):
        """Returns the Zope application instance."""
        return self.debugger


class ZCMLLayer:
    """ZCML-defined test layer"""

    __bases__ = ()

    def __init__(self, config_file, module, name, allow_teardown=False,
        product_config=None):
        self.config_file = config_file
        self.__module__ = module
        self.__name__ = name
        self.allow_teardown = allow_teardown
        self.product_config = product_config

    def setUp(self):
        self.setup = FunctionalTestSetup(
            self.config_file, product_config=self.product_config)

    def tearDown(self):
        self.setup.tearDownCompletely()
        if not self.allow_teardown:
            # Some ZCML directives change globals but are not accompanied
            # with registered CleanUp handlers to undo the changes.  Let
            # packages which use such directives indicate that they do not
            # support tearing down.
            raise NotImplementedError


def defineLayer(name, zcml='ftesting.zcml', allow_teardown=False):
    """Helper function for defining layers.

    Usage: defineLayer('foo')
    
    ATTENTION: Don't use this helper method if a subprocess based setup is 
    involved. Because our sys._getframe will get messed up by the subprocess
    call. This is the case with m01.stub and p01.elasitcsearch as an example.
    Use the plain ZCMLLayer class for define ftesting setup.
    """
    globals = sys._getframe(1).f_globals
    globals[name] = ZCMLLayer(
        os.path.join(os.path.dirname(globals['__file__']), zcml),
        globals['__name__'],
        name,
        allow_teardown=allow_teardown,
        )


def prepareDocTestKeywords(kw):
    globs = kw.setdefault('globs', {})
    if globs.get('getRootFolder') is None:
        globs['getRootFolder'] = getRootFolder

    kwsetUp = kw.get('setUp')
    def setUp(test):
        test.globs['http'] = HTTPCaller()
        FunctionalTestSetup().setUp()
        if kwsetUp is not None:
            kwsetUp(test)
    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        if kwtearDown is not None:
            kwtearDown(test)
        FunctionalTestSetup().tearDown()
    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old
                             | doctest.ELLIPSIS
                             | doctest.REPORT_NDIFF
                             | doctest.NORMALIZE_WHITESPACE)


###############################################################################
#
# test browser
#
###############################################################################

class PublisherConnection(object):
    """A ``mechanize`` compatible connection object with our own HTTPCaller."""

    def __init__(self, host, timeout=None):
        self.caller = HTTPCaller()
        self.host = host

    def set_debuglevel(self, level):
        pass

    def _quote(self, url):
        # the publisher expects to be able to split on whitespace, so we have
        # to make sure there is none in the URL
        return url.replace(' ', '%20')

    def request(self, method, url, body=None, headers=None):
        """Send a request to the publisher.

        The response will be stored in ``self.response``.
        """
        if body is None:
            body = ''

        if url == '':
            url = '/'

        url = self._quote(url)
        # Extract the handle_error option header
        
        if sys.version_info >= (2,5):
            handle_errors_key = 'X-Zope-Handle-Errors'
        else:
            handle_errors_key = 'X-zope-handle-errors'
        handle_errors_header = headers.get(handle_errors_key, True)
        if handle_errors_key in headers:
            del headers[handle_errors_key]

        # translate string to boolean.
        handle_errors = {'False': False}.get(handle_errors_header, True)

        # Construct the headers.
        header_chunks = []
        if headers is not None:
            for header in headers.items():
                header_chunks.append('%s: %s' % header)
            headers = '\n'.join(header_chunks) + '\n'
        else:
            headers = ''

        # Construct the full HTTP request string, since that is what the
        # ``HTTPCaller`` wants.
        request_string = (method + ' ' + url + ' HTTP/1.1\n'
                          + headers + '\n' + body)
        self.response = self.caller(request_string, handle_errors)

    def getresponse(self):
        """Return a ``mechanize`` compatible response.

        The goal of ths method is to convert the Zope Publisher's reseponse to
        a ``mechanize`` compatible response, which is also understood by
        mechanize.
        """
        real_response = self.response._response
        status = real_response.getStatus()
        reason = real_response._reason # XXX add a getReason method

        headers = real_response.getHeaders()
        headers.sort()
        headers.insert(0, ('Status', real_response.getStatusString()))
        headers = '\r\n'.join('%s: %s' % h for h in headers)
        content = real_response.consumeBody()
        return PublisherResponse(content, headers, status, reason)


class PublisherResponse(object):
    """``mechanize`` compatible response object."""

    def __init__(self, content, headers, status, reason):
        self.content = content
        self.status = status
        self.reason = reason
        self.msg = httplib.HTTPMessage(StringIO(headers), 0)
        self.content_as_file = StringIO(self.content)

    def read(self, amt=None):
        return self.content_as_file.read(amt)

    def close(self):
        """To overcome changes in mechanize and socket in python2.5"""
        pass


class PublisherHTTPHandler(mechanize.HTTPHandler):
    """Special HTTP handler to use the Zope Publisher."""

    def http_request(self, req):
        # look at data and set content type
        if req.has_data():
            data = req.get_data()
            if isinstance(data, dict):
                req.add_data(data['body'])
                req.add_unredirected_header('Content-type',
                                            data['content-type'])
        return mechanize.HTTPHandler.do_request_(self, req)

    https_request = http_request

    def http_open(self, req):
        """Open an HTTP connection having a ``mechanize`` request."""
        # Here we connect to the publisher.
        if sys.version_info > (2, 6) and not hasattr(req, 'timeout'):
            # Workaround mechanize incompatibility with Python
            # 2.6. See: LP #280334
            req.timeout = socket._GLOBAL_DEFAULT_TIMEOUT
        return self.do_open(PublisherConnection, req)

    https_open = http_open


class PublisherMechanizeBrowser(mechanize.Browser):
    """Special ``mechanize`` browser using the Zope Publisher HTTP handler."""

    default_schemes = ['http']
    default_others = ['_http_error', '_http_default_error']
    default_features = ['_redirect', '_cookies', '_referer', '_refresh',
                        '_equiv', '_basicauth', '_digestauth']

    def __init__(self, *args, **kws):
        inherited_handlers = ['_unknown', '_http_error',
            '_http_default_error', '_basicauth',
            '_digestauth', '_redirect', '_cookies', '_referer',
            '_refresh', '_equiv', '_gzip']

        self.handler_classes = {"http": PublisherHTTPHandler}
        for name in inherited_handlers:
            self.handler_classes[name] = mechanize.Browser.handler_classes[name]

        kws['request_class'] = kws.get('request_class',
                                       mechanize._request.Request)

        mechanize.Browser.__init__(self, *args, **kws)



class Browser(zope.testbrowser.browser.Browser):
    """A Zope `testbrowser` Browser that uses our PublisherHTTPHandler."""

    def __init__(self, url=None):
        mech_browser = PublisherMechanizeBrowser()
        super(Browser, self).__init__(url=url, mech_browser=mech_browser)


###############################################################################
#
# JSONRPC Test proxy
#
###############################################################################

class JSONRPCTestTransport(z3c.json.transport.Transport):
    """Test transport that delegates to HTTPCaller.

    It can be used like a normal transport, including support for basic 
    authentication.
    """

    verbose = False
    handleErrors = True

    def request(self, host, handler, request_body, verbose=0):
        if not handler:
            handler = '/'
        request = "POST %s HTTP/1.0\n" % (handler,)
        request += "Content-Length: %i\n" % len(request_body)
        request += "Content-Type: application/json\n"

        host, extra_headers, x509 = self.get_host_info(host)
        if extra_headers:
            request += "Authorization: %s\n" % (
                dict(extra_headers)["Authorization"],)

        request += "\n" + request_body
        caller = HTTPCaller()
        response = caller(request, handle_errors=self.handleErrors)

        errcode = response.getStatus()
        errmsg = response.getStatusString()
        # This is not the same way that the normal transport deals with the
        # headers.
        headers = response.getHeaders()

        if errcode != 200:
            raise ProtocolError(host + handler, errcode, errmsg, headers)

        return self._parse_response(
            StringIO(response.getBody()), sock=None)


def JSONRPCTestProxy(uri, transport=None, encoding=None, verbose=None,
    jsonId=None, handleErrors=True, jsonVersion=JSON_RPC_VERSION):
    """A factory that creates a server proxy using the JSONRPCTestTransport 
    by default."""
    if verbose is None:
        verbose = 0
    if transport is None:
        transport = JSONRPCTestTransport()
    if isinstance(transport, JSONRPCTestTransport):
        transport.handleErrors = handleErrors
    return z3c.json.proxy.JSONRPCProxy(uri, transport, encoding, verbose,
        jsonId, jsonVersion)

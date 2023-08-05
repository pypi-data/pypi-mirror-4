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

import tempfile
from types import StringType

import zope.interface
import zope.publisher.browser
from zope.publisher.browser import get_converter
from zope.publisher.browser import CONVERTED
from zope.publisher.browser import SEQUENCE
from zope.publisher.browser import DEFAULT
from zope.publisher.browser import RECORD
from zope.publisher.browser import RECORDS

import z3c.jsonrpc.publisher

import p01.cgi.interfaces
import p01.cgi.parser

from m01.publisher import interfaces

STREAM_SPOOLED_MAX_SIZE = 65536 # zope default
UPLOAD_SPOOLED_MAX_SIZE = 512*1024 # 0.5 MB


class HTTPInputStream(object):
    """Special stream that supports caching the read data.

    This is important, so that we can retry requests.
    
    This implementation also support the new SpooledTemporaryFile
    """
    def __init__(self, stream, environment):
        self.stream = stream
        self.cacheStream = tempfile.SpooledTemporaryFile(
            max_size=STREAM_SPOOLED_MAX_SIZE, mode='w+b')
        size = environment.get('CONTENT_LENGTH')
        # There can be no size in the environment (None) or the size
        # can be an empty string, in which case we treat it as absent.
        if not size:
            size = environment.get('HTTP_CONTENT_LENGTH')
        self.size = size and int(size) or -1

    def getCacheStream(self):
        self.read(self.size)
        self.cacheStream.seek(0)
        return self.cacheStream

    def read(self, size=-1):
        data = self.stream.read(size)
        self.cacheStream.write(data)
        return data

    def readline(self, size=None):
        if size is not None:
            data = self.stream.readline(size)
        else:
            data = self.stream.readline()
        self.cacheStream.write(data)
        return data

    def readlines(self, hint=0):
        data = self.stream.readlines(hint)
        self.cacheStream.write(''.join(data))
        return data


class P01CGIParserMixin(object):
    """P01.cgi parser mixin class"""

    @property
    def tmpFileFactory(self):
        return tempfile.SpooledTemporaryFile

    @property
    def tmpFileFactoryArguments(self):
        """Returns tmp file factory arguments"""
        return {'max_size': UPLOAD_SPOOLED_MAX_SIZE, 'mode': 'w+b'}

    def processInputs(self):
        'See IPublisherRequest'
        fp = None
        if self.method != 'GET':
            # Process self.form if not a GET request.
            fp = self._body_instream

        fslist = p01.cgi.parser.parseFormData(self.method, inputStream=fp,
            environ=self._environ, tmpFileFactory=self.tmpFileFactory,
            tmpFileFactoryArguments=self.tmpFileFactoryArguments)

        if fslist is not None:
            self._BrowserRequest__meth = None
            self._BrowserRequest__tuple_items = {}
            self._BrowserRequest__defaults = {}

            # process all entries in the field storage (form)
            for item in fslist:
                self.__processItem(item)

            if self._BrowserRequest__defaults:
                self._BrowserRequest__insertDefaults()

            if self._BrowserRequest__tuple_items:
                self._BrowserRequest__convertToTuples()

            if self._BrowserRequest__meth:
                self.setPathSuffix((self._BrowserRequest__meth,))

    def __processItem(self, item):
        """Process item in the field storage and use FileUpload."""

        # Note: A field exists for files, even if no filename was
        # passed in and no data was uploaded. Therefore we can only
        # tell by the empty filename that no upload was made.
        key = item.name
        if p01.cgi.interfaces.IMultiPartField.providedBy(item) \
            and item.file is not None and \
            (item.filename is not None and item.filename != ''):
            item = zope.publisher.browser.FileUpload(item)
        else:
            item = item.value

        flags = 0
        converter = None

        # Loop through the different types and set
        # the appropriate flags
        # Syntax: var_name:type_name

        # We'll search from the back to the front.
        # We'll do the search in two steps.  First, we'll
        # do a string search, and then we'll check it with
        # a re search.
        while key:
            pos = key.rfind(":")
            if pos < 0:
                break
            match = self._typeFormat.match(key, pos + 1)
            if match is None:
                break

            key, type_name = key[:pos], key[pos + 1:]

            # find the right type converter
            c = get_converter(type_name, None)

            if c is not None:
                converter = c
                flags |= CONVERTED
            elif type_name == 'list':
                flags |= SEQUENCE
            elif type_name == 'tuple':
                self._BrowserRequest__tuple_items[key] = 1
                flags |= SEQUENCE
            elif (type_name == 'method' or type_name == 'action'):
                if key:
                    self._BrowserRequest__meth = key
                else:
                    self._BrowserRequest__meth = item
            elif (type_name == 'default_method'
                    or type_name == 'default_action') and \
                    not self._BrowserRequest__meth:
                if key:
                    self._BrowserRequest__meth = key
                else:
                    self._BrowserRequest__meth = item
            elif type_name == 'default':
                flags |= DEFAULT
            elif type_name == 'record':
                flags |= RECORD
            elif type_name == 'records':
                flags |= RECORDS
            elif type_name == 'ignore_empty' and not item:
                # skip over empty fields
                return

        # Make it unicode if not None
        if key is not None:
            key = self._decode(key)

        if type(item) == StringType:
            item = self._decode(item)

        if flags:
            self._BrowserRequest__setItemWithType(key, item, flags, converter)
        else:
            self._BrowserRequest__setItemWithoutType(key, item)


class RequestMixin(object):
    """Request mixin class for ZODB less publications.
    
    Note: you need to define __slots__ if you like to expose the _app
    in your request mixin class.
    """

    app = property(lambda self: self._app)
    appURL = property(lambda self: self.getApplicationURL())

    def setPublication(self, pub):
        self._app = pub.app
        super(RequestMixin, self).setPublication(pub)


class BrowserRequest(RequestMixin, P01CGIParserMixin,
    zope.publisher.browser.BrowserRequest):
    """BrowserRequest which can handle very large and fast file upload.

    This request uses th new SpooledTemporaryFile which will rollover if we
    receive a large input stream.

    Another improvment is the parseFormData method which replaces the default
    cgi.FieldStorage. This parser implementation fixes some issues in the
    original implementation like:

    - reads the full file data into memory in FieldStorage.__repr__ method

    """

    zope.interface.implements(interfaces.IBrowserRequest)

    def __init__(self, body_instream, environ, response=None):
        super(BrowserRequest, self).__init__(body_instream, environ, response)
        self._body_instream = HTTPInputStream(body_instream, self._orig_env)

    __slots__ = (
        '_root',
        )


class JSONRPCRequest(RequestMixin, 
    z3c.jsonrpc.publisher.JSONRPCRequest):
    """JSONRPCRequest."""

    zope.interface.implements(interfaces.IJSONRPCRequest)

    __slots__ = (
        '_root',
        )

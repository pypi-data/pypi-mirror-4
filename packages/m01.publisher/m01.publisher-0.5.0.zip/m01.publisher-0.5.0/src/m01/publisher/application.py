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

import time

import zope.interface
import zope.component

from m01.publisher import interfaces


class Application(object):
    """Application base class for ZODB less publications."""

    zope.interface.implements(interfaces.IApplication)

    __name__ = __parent__ = None

    def __init__(self):
        self.start_time = time.time()

    def getStartTime(self):
        return self.start_time

    def getSiteManager(self):
        return zope.component.getGlobalSiteManager()

    def setSiteManager(self, sm):
        raise NotImplementedError("setSiteManager is not supported")

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)
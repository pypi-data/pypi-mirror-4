##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Resource base class and AbsoluteURL adapter
"""

import zope.interface
import zope.component
import zope.component.hooks
from zope.traversing.browser.interfaces import IAbsoluteURL
import zope.traversing.browser.absoluteurl

import zope.browserresource.interfaces

from z3c.jsonrpc.interfaces import IJSONRPCRequest


# XXX: move this to z3c.jsonrpc, otherwise we can't lookup correct resource
#      path
class AbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):

    zope.interface.implementsOnly(IAbsoluteURL)
    zope.component.adapts(zope.browserresource.interfaces.IResource,
        IJSONRPCRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _createUrl(self, baseUrl, name):
        return "%s/@@/%s" % (baseUrl, name)

    def __str__(self):
        name = self.context.__name__
        if name.startswith('++resource++'):
            name = name[12:]

        site = zope.component.hooks.getSite()
        base = zope.component.queryMultiAdapter((site, self.request), IAbsoluteURL,
            name="resource")
        if base is None:
            url = str(zope.component.getMultiAdapter((site, self.request), IAbsoluteURL))
        else:
            url = str(base)

        return self._createUrl(url, name)

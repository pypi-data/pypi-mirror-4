##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Browser UI code.
"""
import zope.component
import zope.interface
import zope.location
import zope.traversing.api
import zope.traversing.browser
from zope.proxy import sameProxiedObjects
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.interfaces import IContainmentRoot

from z3c.breadcrumb import interfaces


@zope.interface.implementer(interfaces.IBreadcrumbs)
class Breadcrumbs(zope.location.Location):
    """Breadcrumbs implementation using IBreadcrumb adapters."""
    zope.component.adapts(zope.interface.Interface, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    def __getParent(self):
        return getattr(self, '_parent', self.context)

    def __setParent(self, parent):
        self._parent = parent

    __parent__ = property(__getParent, __setParent)

    @property
    def crumbs(self):
        request = self.request

        objects = []
        for obj in ( [self.context] +
                     list(zope.traversing.api.getParents(self.context)) ):
            objects.append(obj)
            if sameProxiedObjects(obj, request.getVirtualHostRoot()) or \
                    isinstance(obj, Exception):
                break

        objects.reverse()
        for object in objects:
            info = zope.component.queryMultiAdapter(
                (object, self.request), interfaces.IBreadcrumb)
            if info is None:
                continue
            yield {'name': info.name,
                   'url': info.url,
                   'activeURL': info.activeURL}


@zope.interface.implementer(interfaces.IBreadcrumb)
class GenericBreadcrumb(object):
    """A generic breadcrumb adapter."""
    zope.component.adapts(zope.interface.Interface, IHTTPRequest)

    # See interfaces.IBreadcrumb
    activeURL = True

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def name(self):
        """See interfaces.IBreadcrumb"""
        name = getattr(self.context, 'title', '')
        if not name:
            name = getattr(self.context, '__name__', '')
        if not name and IContainmentRoot.providedBy(self.context):
            name = 'top'
        return name

    @property
    def url(self):
        """See interfaces.IBreadcrumb"""
        return zope.traversing.browser.absoluteURL(self.context, self.request)


def CustomNameBreadcrumb(name):
    return type('CustomNameBreadcrumb(%r)' %name,
                (GenericBreadcrumb,), {'name': name})

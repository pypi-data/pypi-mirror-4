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
"""Interfaces
"""
import zope.interface
import zope.schema


class IBreadcrumbs(zope.interface.Interface):
    """An object providing breadcrumbs.

    This object will use the ``IBreadcrumb`` adapter to get its
    information from each breadcrumb name.
    """

    crumbs = zope.interface.Attribute('An iterable of all breadcrumbs.')


class IBreadcrumb(zope.interface.Interface):
    """Provides pieces of breadcrumb information about a item."""

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'The name of the breadcrumb.',
        required=True)

    url = zope.schema.URI(
        title=u'URL',
        description=u'The url of the breadcrumb.',
        required=True)

    activeURL = zope.schema.Bool(
        title=u'Active',
        description=u'Tells whether the breadcrumb link should be active.',
        required=True,
        default=True)


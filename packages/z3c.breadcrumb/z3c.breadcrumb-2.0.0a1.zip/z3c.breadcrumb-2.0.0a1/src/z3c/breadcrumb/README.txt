======
README
======

The z3c.breadcrumb package provides base classes for breadcrumb
implementations. It allows you to write adapters for each content object which
provides it's own rule for providing the breadcrumb name, url and selection.

Let's do some imports we will use later.

  >>> import zope.interface
  >>> import zope.component
  >>> from zope.publisher.interfaces.http import IHTTPRequest
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.traversing.browser import absoluteURL
  >>> from zope.container import contained
  >>> from z3c.breadcrumb import interfaces
  >>> from z3c.breadcrumb import browser


IBreadcrumb
-----------

Let's define a interface and a content object.

  >>> class IOffice(zope.interface.Interface):
  ...     """Office interface."""

  >>> @zope.interface.implementer(IOffice)
  ... class Office(contained.Contained):
  ...     def __init__(self, label):
  ...         self.label = label
  ...         self.activeURL = True

  >>> office = Office(u'Zope Foundation')
  >>> office.__name__ = u'ZF'

There is a generic breadcrumb implementation which is registered by
default. If we do not implement a custom IBreadcrumb the generic adapter will
return the ``title`` or ``__name__`` of the item. Let's register the default
adapter, this is normally done in ``configure.zcml``:

  >>> zope.component.provideAdapter(browser.GenericBreadcrumb)

And see what we get:

  >>> request = TestRequest()
  >>> breadcrumb = zope.component.getMultiAdapter((office, request),
  ...     interfaces.IBreadcrumb)
  >>> breadcrumb.name
  u'ZF'

We can also implement a custom ``IBreadcrumb`` adapter and provide another
name for the breadcrumb name:

  >>> @zope.interface.implementer(interfaces.IBreadcrumb)
  ... @zope.component.adapter(IOffice, IHTTPRequest)
  ... class BreadcrumbForOffice(object):
  ...
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request
  ...
  ...     @property
  ...     def name(self):
  ...         return self.context.label
  ...
  ...     @property
  ...     def url(self):
  ...         return absoluteURL(self.context, self.request)
  ...
  ...     @property
  ...     def activeURL(self):
  ...         return self.context.activeURL

Let's register the custom ``IBreadcrumb`` adapter for IOffice:

  >>> zope.component.provideAdapter(BreadcrumbForOffice)

And check the new breadcrumb name:

  >>> breadcrumb = zope.component.getMultiAdapter((office, request),
  ...     interfaces.IBreadcrumb)
  >>> breadcrumb.name
  u'Zope Foundation'


CustomNameBreadcrumb
--------------------

Let's define another interface and a content object.

  >>> class IOfficeContainer(zope.interface.Interface):
  ...     """Container of offices."""

  >>> @zope.interface.implementer(IOfficeContainer)
  ... class OfficeContainer(contained.Contained):
  ...     pass

  >>> offices = OfficeContainer()
  >>> offices.__name__ = u'offices'

If the custom name for this kind of object is always the same it would quickly
get tedious to write a full IBreadcrumb implementation.  As a shortcut you
can use CustomNameBreadcrumb to get an adapter that acts like
GenericBreadcrumb, but returns the name you want.

  >>> adapter = browser.CustomNameBreadcrumb(u'Offices')
  >>> adapter
  <class 'z3c.breadcrumb.browser.CustomNameBreadcrumb(u'Offices')'>
  >>> zope.component.provideAdapter(adapter,
  ...     adapts=(IOfficeContainer, IHTTPRequest))

  >>> breadcrumb = zope.component.getMultiAdapter((offices, request),
  ...     interfaces.IBreadcrumb)
  >>> breadcrumb.name
  u'Offices'


IBreadcrumbs
------------

There is also a IBreadcrumbs adapter which knows how to collect breadcrumb
informations for each item he traverses. We need to setup a little bit of
infrastructure:

  >>> root = rootFolder
  >>> root['office'] = office

Register the IBreadcrumbs adapter:

  >>> zope.component.provideAdapter(browser.Breadcrumbs,
  ...     (zope.interface.Interface, zope.interface.Interface),
  ...     interfaces.IBreadcrumbs)


Now we can collect breadcrumbs for our items. You can see the url is correct
and the label ``Zope Foundation`` is collected by the custom IBreadcrumb
adapter:

  >>> breadcrumbs = zope.component.getMultiAdapter((office, request),
  ...     interfaces.IBreadcrumbs)
  >>> from pprint import pprint
  >>> pprint(list(breadcrumbs.crumbs))
  [{'activeURL': True,
    'name': 'top',
    'url': 'http://127.0.0.1'},
   {'activeURL': True,
    'name': 'Zope Foundation',
    'url': 'http://127.0.0.1/office'}]

  >>> breadcrumbs.__parent__ is office
  True

Default breadcrumbs stops on virtual host root

  >>> request._vh_root = office
  >>> pprint(list(breadcrumbs.crumbs))
  [{'activeURL': True,
    'name': 'Zope Foundation',
    'url': 'http://127.0.0.1'}]

If the breadcrumb of an item is a Null-adapter, then the item is ignored.

  >>> from zope.traversing.interfaces import IContainmentRoot
  >>> zope.component.provideAdapter(
  ...     lambda c, r: None,
  ...     (IContainmentRoot, IHTTPRequest),
  ...     interfaces.IBreadcrumb)

  >>> request = TestRequest()
  >>> breadcrumbs = zope.component.getMultiAdapter(
  ...     (office, request), interfaces.IBreadcrumbs)
  >>> pprint(list(breadcrumbs.crumbs))
  [{'activeURL': True,
    'name': 'Zope Foundation',
    'url': 'http://127.0.0.1/office'}]

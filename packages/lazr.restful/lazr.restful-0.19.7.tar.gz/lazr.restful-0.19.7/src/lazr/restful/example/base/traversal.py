# Copyright 2009 Canonical Ltd.  All rights reserved.

"""Traversal rules for the LAZR example web service."""

__metaclass__ = type
__all__ = [
    'BelowRootAbsoluteURL',
    'CookbookSetTraverse',
    'RootAbsoluteURL',
    'TraverseWithGet',
    ]


from urllib import unquote
from zope.component import adapts
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.browser import absoluteURL, AbsoluteURL

import grokcore.component

from lazr.restful.example.base.interfaces import ICookbookSet, IHasGet
from lazr.restful.example.base.root import CookbookWebServiceObject
from lazr.restful.simple import (
    RootResourceAbsoluteURL,
    SimulatedWebsiteRequest,
    )
from lazr.restful import RedirectResource


def web_service_request_to_web_site_request(web_service_request):
    """Create a simulated website request for generating web_link."""
    body = web_service_request.bodyStream.getCacheStream()
    environ = dict(web_service_request.environment)
    return SimulatedWebsiteRequest(body, environ)


class RootAbsoluteURL(RootResourceAbsoluteURL):
    """A technique for generating the service's root URL.

    This class contains no code of its own. It's defined so that grok
    will pick it up.
    """


class BelowRootAbsoluteURL(AbsoluteURL):
    """A technique for generating a root URL given an ILocation.

    This class contains no code of its own. It's defined so that
    grok will pick it up.
    """


class TraverseWithGet(grokcore.component.MultiAdapter):
    """A simple IPublishTraverse that uses the get() method."""
    grokcore.component.adapts(IHasGet, IDefaultBrowserLayer)
    grokcore.component.implements(IPublishTraverse)

    def __init__(self, context, request):
        self.context = context

    def publishTraverse(self, request, name):
        name = unquote(name)
        value = self.context.get(name)
        if value is None:
            raise NotFound(self, name)
        return value


class CookbookSetTraverse(TraverseWithGet):
    """An IPublishTraverse that implements a custom redirect."""
    grokcore.component.adapts(ICookbookSet, IDefaultBrowserLayer)
    grokcore.component.implements(IPublishTraverse)

    def publishTraverse(self, request, name):
        if name == 'featured':
            url = absoluteURL(self.context.featured, request)
            return RedirectResource(url, request)
        elif name == 'featured-invalid':
            # This is to enable a test case in which the redirect URL
            # contains characters not valid in URLs.
            url = absoluteURL(self.context.featured, request) + "{invalid}"
            return RedirectResource(url, request)
        else:
            return super(CookbookSetTraverse, self).publishTraverse(
                request, name)

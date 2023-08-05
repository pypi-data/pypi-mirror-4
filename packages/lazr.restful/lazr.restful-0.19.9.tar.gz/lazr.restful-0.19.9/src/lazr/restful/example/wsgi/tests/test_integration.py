# Copyright 2008 Canonical Ltd.  All rights reserved.

"""Test harness for doctests for lazr.restful example WSGI service."""

__metaclass__ = type
__all__ = []

import os
import doctest
from pkg_resources import resource_filename

from zope.component import getUtility
from zope.configuration import xmlconfig
from zope.testing.cleanup import cleanUp
from van.testing.layer import zcml_layer, wsgi_intercept_layer

from lazr.restful.example.wsgi.root import WSGIExampleWebServiceRootResource
from lazr.restful.interfaces import IWebServiceConfiguration
from lazr.restful.simple import Publication
from lazr.restful.testing.webservice import WebServiceApplication


DOCTEST_FLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_NDIFF)

class FunctionalLayer:
    zcml = os.path.abspath(resource_filename(
        'lazr.restful.example.wsgi', 'site.zcml'))
zcml_layer(FunctionalLayer)


class WSGILayer(FunctionalLayer):
    @classmethod
    def make_application(self):
        getUtility(IWebServiceConfiguration).hostname = "wsgidemo.dev"
        getUtility(IWebServiceConfiguration).port = None
        root = WSGIExampleWebServiceRootResource()
        return WebServiceApplication(root, Publication)
wsgi_intercept_layer(WSGILayer)


def additional_tests():
    """See `zope.testing.testrunner`."""
    tests = sorted(
        [name
         for name in os.listdir(os.path.dirname(__file__))
         if name.endswith('.txt')])
    suite = doctest.DocFileSuite(optionflags=DOCTEST_FLAGS, *tests)
    suite.layer = WSGILayer
    return suite

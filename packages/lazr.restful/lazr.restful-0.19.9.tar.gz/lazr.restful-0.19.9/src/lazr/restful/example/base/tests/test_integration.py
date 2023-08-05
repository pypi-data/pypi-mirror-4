# Copyright 2008 Canonical Ltd.  All rights reserved.

"""Test harness for LAZR doctests."""

__metaclass__ = type
__all__ = []

import os
import doctest
from pkg_resources import resource_filename

from zope.configuration import xmlconfig
from zope.testing.cleanup import cleanUp
from van.testing.layer import zcml_layer, wsgi_intercept_layer

from lazr.restful.example.base.root import CookbookServiceRootResource
from lazr.restful.testing.webservice import (
    WebServiceTestPublication, WebServiceApplication)


class CookbookWebServiceTestPublication(WebServiceTestPublication):
    def getApplication(self, request):
        return CookbookServiceRootResource()


DOCTEST_FLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_NDIFF)

class FunctionalLayer:
    allow_teardown = False
    zcml = os.path.abspath(resource_filename('lazr.restful', 'ftesting.zcml'))
zcml_layer(FunctionalLayer)


class WSGILayer(FunctionalLayer):
    @classmethod
    def make_application(self):
        return WebServiceApplication({}, CookbookWebServiceTestPublication)
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

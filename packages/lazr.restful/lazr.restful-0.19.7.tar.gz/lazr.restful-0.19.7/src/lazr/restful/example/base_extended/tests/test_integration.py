# Copyright 20010 Canonical Ltd.  All rights reserved.

"""Test harness for LAZR doctests."""

__metaclass__ = type
__all__ = []

import os
import doctest
from pkg_resources import resource_filename

from van.testing.layer import zcml_layer, wsgi_intercept_layer

from lazr.restful.example.base.tests.test_integration import (
    CookbookWebServiceTestPublication, DOCTEST_FLAGS)
from lazr.restful.testing.webservice import WebServiceApplication


class FunctionalLayer:
    allow_teardown = False
    zcml = os.path.abspath(resource_filename(
        'lazr.restful.example.base_extended', 'site.zcml'))
zcml_layer(FunctionalLayer)


class WSGILayer(FunctionalLayer):
    @classmethod
    def make_application(self):
        return WebServiceApplication({}, CookbookWebServiceTestPublication)
wsgi_intercept_layer(WSGILayer)


def additional_tests():
    """See `zope.testing.testrunner`."""
    tests = ['../README.txt']
    suite = doctest.DocFileSuite(optionflags=DOCTEST_FLAGS, *tests)
    suite.layer = WSGILayer
    return suite

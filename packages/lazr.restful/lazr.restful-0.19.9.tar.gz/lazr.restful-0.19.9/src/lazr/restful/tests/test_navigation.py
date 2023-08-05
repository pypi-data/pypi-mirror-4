# Copyright 2008 Canonical Ltd.  All rights reserved.

"""Tests of lazr.restful navigation."""

__metaclass__ = type

import unittest

from zope.component import getSiteManager
from zope.interface import Interface, implements
from zope.publisher.interfaces import NotFound
from zope.schema import Text
from zope.testing.cleanup import cleanUp

from lazr.restful.fields import Reference
from lazr.restful.interfaces import (
    IEntry,
    IWebServiceClientRequest,
    )
from lazr.restful.simple import Publication
from lazr.restful.testing.webservice import FakeRequest


class IChild(Interface):
    """Interface for a simple entry."""
    one = Text(title=u'One')
    two = Text(title=u'Two')


class IParent(Interface):
    """Interface for a simple entry that contains another entry."""
    three = Text(title=u'Three')
    child = Reference(schema=IChild)


class Child:
    """A simple implementation of IChild."""
    implements(IChild)
    one = u'one'
    two = u'two'


class ChildEntry:
    """Implementation of an entry wrapping a Child."""
    schema = IChild
    def __init__(self, context, request):
        self.context = context


class Parent:
    """A simple implementation of IParent."""
    implements(IParent)
    three = u'three'
    child = Child()


class ParentEntry:
    """Implementation of an entry wrapping a Parent, containing a Child."""
    schema = IParent

    def __init__(self, context, request):
        self.context = context

    @property
    def child(self):
        return self.context.child


class FakeRequestWithEmptyTraversalStack(FakeRequest):
    """A fake request satisfying `traverseName()`."""

    def getTraversalStack(self):
        return ()


class NavigationTestCase(unittest.TestCase):

    def setUp(self):
        # Register ChildEntry as the IEntry implementation for IChild.
        sm = getSiteManager()
        sm.registerAdapter(
            ChildEntry, [IChild, IWebServiceClientRequest], provided=IEntry)

        # Register ParentEntry as the IEntry implementation for IParent.
        sm.registerAdapter(
            ParentEntry, [IParent, IWebServiceClientRequest], provided=IEntry)

    def tearDown(self):
        cleanUp()

    def test_toplevel_navigation(self):
        # Test that publication can reach sub-entries.
        publication = Publication(None)
        request = FakeRequestWithEmptyTraversalStack(version='trunk')
        obj = publication.traverseName(request, Parent(), 'child')
        self.assertEqual(obj.one, 'one')

    def test_toplevel_navigation_without_subentry(self):
        # Test that publication raises NotFound when subentry attribute
        # returns None.
        request = FakeRequestWithEmptyTraversalStack(version='trunk')
        parent = Parent()
        parent.child = None
        publication = Publication(None)
        self.assertRaises(
            NotFound, publication.traverseName,
            request, parent, 'child')


def additional_tests():
    return unittest.TestLoader().loadTestsFromName(__name__)

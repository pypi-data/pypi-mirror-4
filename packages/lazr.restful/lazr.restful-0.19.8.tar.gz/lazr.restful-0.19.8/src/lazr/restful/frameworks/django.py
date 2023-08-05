# Copyright 2009 Canonical Ltd.  All rights reserved.

"""Helpers for publishing Django model objects in lazr.restful services."""

__metaclass__ = type
__all__ = [
    'DjangoLocation',
    'DjangoWebServiceConfiguration',
    'IDjangoLocation',
    'ManagerSequencer',
    ]

import settings

import martian

from zope.interface import Interface, implements
from zope.interface.common.sequence import IFiniteSequence
from zope.location.interfaces import ILocation
from zope.schema import getFieldsInOrder
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL

import grokcore.component
# Without this trickery, this module (called "django") will mask the
# real Django modules. We could use "from __future__ import
# absolute_import", but that would not work with Python 2.4.
ObjectDoesNotExist = __import__(
    'django.core.exceptions', {}).core.exceptions.ObjectDoesNotExist
Manager = __import__(
    'django.db.models.manager', {}).db.models.manager.Manager

from lazr.restful import directives
from lazr.restful.interfaces import (
    IWebServiceLayer, IWebServiceClientRequest, IWebServiceConfiguration)
from lazr.restful.error import NotFoundView
from lazr.restful.simple import BaseWebServiceConfiguration


class DjangoWebServiceConfiguration(BaseWebServiceConfiguration):
    """Retrieve configuration options from the Django settings module.

    Create an empty subclass of this class, and you can configure your
    web service from your settings.py file.
    """


class DjangoConfigurationGrokker(martian.ClassGrokker):
    """Pull lazr.restful configuration from the Django 'settings' module.

    Subclass DjangoWebServiceConfiguration to get a configuration class
    that can be overridden from your Django 'settings' module.
    """
    martian.component(DjangoWebServiceConfiguration)
    def execute(self, cls, config, *kw):
        for name, field in getFieldsInOrder(IWebServiceConfiguration):
            settings_name = "LAZR_RESTFUL_" + name.upper()
            value = getattr(settings, settings_name, None)
            if value is not None:
                setattr(cls, name, value)
        return True


class IDjangoLocation(Interface):
    """Like Zope's ILocation, but adapted to work with Django.

    The problem with ILocation is that you have to define __name__,
    and the Django metaclass won't let you assign a property to
    __name__.
    """

    def __url_path__(self):
        """The URL path for this object."""

    def __parent__(self):
        """This object's parent in the object tree."""

# We want a raised django.core.exceptions.ObjectDoesNotExist
# object to result in a 404 status code. But we don't
# control that class definition, so we can't annotate it.
# Instead, we define an adapter from that exception class to the
# NotFoundView
grokcore.component.global_adapter(
    NotFoundView, (ObjectDoesNotExist, IWebServiceClientRequest),
    Interface, name="index.html")


class DjangoAbsoluteURL(AbsoluteURL):
    """An AbsoluteURL implementation for Django."""
    directives.location_interface(IDjangoLocation)


class DjangoLocation(object):
    """Adapts Django model objects to ILocation.

    See `IDjangoLocation` for why Django model objects can't implement
    ILocation directly.
    """
    implements(ILocation)

    def __init__(self, context):
        self.context = context

    @property
    def __parent__(self):
        return self.context.__parent__

    @property
    def __name__(self):
        return self.context.__url_path__
grokcore.component.global_adapter(DjangoLocation, IDjangoLocation, ILocation)


class ManagerSequencer(object):
    """Makes a Django manager object usable with lazr.batchnavigator.

    IFiniteSequence requires that we implement __len__, and either
    __getitem__ or __iter__. We implement all three.
    """
    implements(IFiniteSequence)

    def __init__(self, manager):
        """Initialize with respect to a Django manager object."""
        self.manager = manager

    def __iter__(self):
        """Return an iterator over the dataset."""
        return self.manager.iterator()

    def __getitem__(self, index_or_slice):
        """Slice the dataset."""
        return self.manager.all()[(index_or_slice)]

    def __len__(self):
        """Return the length of the dataset."""
        return self.manager.count()
grokcore.component.global_adapter(ManagerSequencer, Manager, IFiniteSequence)

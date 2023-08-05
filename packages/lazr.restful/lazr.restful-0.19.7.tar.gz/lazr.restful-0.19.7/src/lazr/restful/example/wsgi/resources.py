__metaclass__ = type

__all__ = ['IKeyValuePair',
           'IPairSet',
           'KeyValuePair',
           'PairSet']

from zope.component import getUtility
from zope.interface import Attribute, implements
from zope.schema import Text
from zope.location.interfaces import ILocation

from lazr.restful.declarations import (
    collection_default_content, export_as_webservice_collection,
    export_as_webservice_entry, exported)
from lazr.restful.interfaces import IServiceRootResource
from lazr.restful.simple import TraverseWithGet


class IKeyValuePair(ILocation):
    export_as_webservice_entry()
    key = exported(Text(title=u"The key"))
    value = exported(Text(title=u"The value"))


class IPairSet(ILocation):
    export_as_webservice_collection(IKeyValuePair)

    @collection_default_content()
    def getPairs():
        """Return the key-value pairs."""

    def get(request, name):
        """Retrieve a key-value pair by its key."""


class KeyValuePair(object):
    """An object representing a key-value pair"""
    implements(IKeyValuePair, ILocation)

    def __init__(self, set, key, value):
        self.set = set
        self.key = key
        self.value = value

    # ILocation implementation
    @property
    def __parent__(self):
        return self.set

    @property
    def __name__(self):
        return self.key


class PairSet(TraverseWithGet):
    """A repository for key-value pairs."""
    implements(IPairSet, ILocation)

    def __init__(self):
        self.pairs = []

    def getPairs(self):
        return self.pairs

    def get(self, request, name):
        pairs = [pair for pair in self.pairs if pair.key == name]
        if len(pairs) == 1:
            return pairs[0]
        return None

    # ILocation implementation
    @property
    def __parent__(self):
        return getUtility(IServiceRootResource)

    @property
    def __name__(self):
        return 'pairs'

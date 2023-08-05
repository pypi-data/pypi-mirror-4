# Copyright 2008 Canonical Ltd.  All rights reserved.

"""LAZR zope.schema.IField implementation."""

__metaclass__ = type
__all__ = [
    'CollectionField',
    'Reference',
    'ReferenceChoice',
    ]

from zope.interface import implements
from zope.schema import Choice, Field, Object
from zope.schema.interfaces import IObject, SchemaNotProvided
from zope.schema._field import AbstractCollection

from lazr.restful.interfaces import (
    ICollectionField, IReference, IReferenceChoice)


class CollectionField(AbstractCollection):
    """A collection associated with an entry."""
    # We subclass AbstractCollection instead of List because List
    # has a _type of list, and we don't want to have to implement list
    # semantics for this class.
    implements(ICollectionField)

    def __init__(self, *args, **kwargs):
        """A generic collection field.

        The readonly property defaults to True since these fields are usually
        for collections of things linked to an object, and these collections
        are managed through a dedicated API.
        """
        kwargs.setdefault('readonly', True)
        super(CollectionField, self).__init__(*args, **kwargs)


class Reference(Object):
    """An Object-like field which doesn't validate all fields of the schema.

    Unlike Object, which does call _validate_fields(self.schema, value) to
    validate all fields, this field will simply call the _validate() method of
    the Field class and then check that the given value provides the specified
    schema.
    """
    implements(IReference)

    def _validate(self, value):
        Field._validate(self, value)
        if not self.schema.providedBy(value):
            raise SchemaNotProvided()


class ReferenceChoice(Choice):
    """A choice among objects."""
    implements(IReferenceChoice)

    def __init__(self, *args, **kwargs):
        """Initialize a choice among a certain kind of object.
        This field can provide more information in a WADL description
        than a standard Choice field.

        This constructor takes the same parameters as the Choice
        constructor, plus a 'schema' keyword parameter.

        :param schema: What kind of object makes up the Choice's vocabulary.
                       The default is IObject.
        """
        schema = kwargs.pop('schema', IObject)
        self.schema = schema
        super(ReferenceChoice, self).__init__(*args, **kwargs)

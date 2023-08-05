# Copyright 2009 Canonical Ltd.  All rights reserved.
# pylint: disable-msg=E0211,E0213

"""Interface objects for the LAZR example web service."""

__metaclass__ = type
__all__ = ['AlreadyNew',
           'Cuisine',
           'ICookbook',
           'ICookbookSet',
           'IDish',
           'IDishSet',
           'IFileManager',
           'IHasGet',
           'IFileManagerBackedByteStorage',
           'IRecipe',
           'IRecipeSet',
           'NameAlreadyTaken']

from zope.interface import Attribute, Interface
from zope.schema import Bool, Bytes, Choice, Date, Float, Int, TextLine, Text
from zope.location.interfaces import ILocation

from lazr.enum import EnumeratedType, Item

from lazr.restful.fields import CollectionField, Reference
from lazr.restful.interfaces import IByteStorage, ITopLevelEntryLink
from lazr.restful.declarations import (
    collection_default_content, export_as_webservice_collection,
    export_as_webservice_entry, export_destructor_operation,
    export_factory_operation, export_read_operation, export_write_operation,
    exported, operation_parameters, operation_returns_collection_of,
    operation_returns_entry, webservice_error)


class AlreadyNew(Exception):
    """A cookbook's name prohibits the cheap 'The New' trick."""
    webservice_error(400)


class NameAlreadyTaken(Exception):
    """The name given for a cookbook is in use by another cookbook."""
    webservice_error(409)


class WhitespaceStrippingTextLine(TextLine):
    """A TextLine that won't abide leading or trailing whitespace."""

    def set(self, object, value):
        """Strip whitespace before setting."""
        if value is not None:
            value = value.strip()
        super(WhitespaceStrippingTextLine, self).set(object, value)


class Cuisine(EnumeratedType):
    """A vocabulary for cuisines."""

    GENERAL = Item("General", "General cooking")
    VEGETARIAN = Item("Vegetarian", "Vegetarian cooking")
    AMERICAN = Item("American", "Traditional American cooking")
    DESSERT = Item("Dessert", "Desserts")
    FRANCAISE = Item("Fran\xc3\xa7aise".decode("utf-8"),
                    "Cuisine fran\xc3\xa7aise".decode("utf-8"))


class IHasGet(Interface):
    """A marker interface objects that implement traversal with get()."""
    def get(name):
        """Traverse to a contained object."""


class IDish(ILocation):
    """A dish, annotated for export to the web service."""
    export_as_webservice_entry(plural_name='dishes')
    name = exported(TextLine(title=u"Name", required=True))
    recipes = exported(CollectionField(
            title=u"Recipes in this cookbook",
            value_type=Reference(schema=Interface)))

    def removeRecipe(recipe):
        """Remove one of this dish's recipes."""


class IRecipe(ILocation):
    """A recipe, annotated for export to the web service."""
    export_as_webservice_entry()
    id = exported(Int(title=u"Unique ID", required=True))
    dish = exported(Reference(title=u"Dish", schema=IDish))
    cookbook = exported(Reference(title=u"Cookbook", schema=Interface))
    instructions = exported(Text(title=u"How to prepare the recipe",
                                 required=True))
    private = exported(Bool(title=u"Whether the public can see this recipe.",
                       default=False))
    prepared_image = exported(
        Bytes(0, 5000, title=u"An image of the prepared dish.",
              readonly=True))

    @export_destructor_operation()
    def delete():
        """Delete the recipe."""


class ICookbook(IHasGet, ILocation):
    """A cookbook, annotated for export to the web service."""
    export_as_webservice_entry()
    name = exported(TextLine(title=u"Name", required=True))
    copyright_date = exported(
        Date(title=u"Copyright Date",
             description=u"The copyright date for this work."), readonly=True)
    description = exported(
        WhitespaceStrippingTextLine(title=u"Description", required=False))
    revision_number = exported(
        Int(title=u"A record of the number of times "
                   "this cookbook has been modified."))
    confirmed = exported(Bool(
        title=u"Whether this information has been confirmed",
        default=False))
    cuisine = exported(Choice(
        vocabulary=Cuisine, title=u"Cuisine", required=False, default=None))
    last_printing = exported(
        Date(title=u"Last printing",
             description=u"The date of this work's most recent printing."))
    # Don't try this at home! Float is a bad choice for a 'price'
    # field because it's imprecise. Decimal is a better choice. But
    # this is just an example and we need a Float field, so...
    price = exported(Float(title=u"Retail price of the cookbook"))
    recipes = exported(CollectionField(title=u"Recipes in this cookbook",
                                       value_type=Reference(schema=IRecipe)))
    cover = exported(
        Bytes(0, 5000, title=u"An image of the cookbook's cover."))

    @operation_parameters(
        search=TextLine(title=u"String to search for in recipe name."))
    @operation_returns_collection_of(IRecipe)
    @export_read_operation()
    def find_recipes(search):
        """Search for recipes in this cookbook."""

    @operation_parameters(
        dish=Reference(title=u"Dish to search for.", schema=IDish))
    @operation_returns_entry(IRecipe)
    @export_read_operation()
    def find_recipe_for(dish):
        """Find a recipe in this cookbook for a given dish."""

    @export_write_operation()
    def make_more_interesting():
        """Alter a cookbook to make it seem more interesting."""

    def removeRecipe(recipe):
        """Remove one of this cookbook's recipes."""

    @operation_parameters(cover=Bytes(title=u"New cover"))
    @export_write_operation()
    def replace_cover(cover):
        """Replace the cookbook's cover."""


# Resolve dangling references
IDish['recipes'].value_type.schema = IRecipe
IRecipe['cookbook'].schema = ICookbook


class ICookbookSubclass(ICookbook):
    """A published subclass of ICookbook.

    This entry interface is never used, but it acts as a test case for
    a published entry interface that subclasses another published
    entry interface.
    """
    export_as_webservice_entry()


class IFeaturedCookbookLink(ITopLevelEntryLink):
    """A marker interface."""


class ICookbookSet(IHasGet):
    """The set of all cookbooks, annotated for export to the web service."""
    export_as_webservice_collection(ICookbook)

    @collection_default_content()
    def getCookbooks():
        """Return the list of cookbooks."""

    @operation_parameters(
        search=TextLine(title=u"String to search for in recipe name."),
        vegetarian=Bool(title=u"Whether or not to limit the search to "
                        "vegetarian cookbooks.", default=False))
    @operation_returns_collection_of(IRecipe)
    @export_read_operation()
    def find_recipes(search, vegetarian):
        """Search for recipes across cookbooks."""

    @operation_parameters(
        cuisine=Choice(vocabulary=Cuisine,
                       title=u"Cuisine to search for in recipe name."))
    @operation_returns_collection_of(ICookbook)
    @export_read_operation()
    def find_for_cuisine(cuisine):
        """Search for cookbooks of a given cuisine."""

    @export_factory_operation(
        ICookbook, ['name', 'description', 'cuisine', 'copyright_date',
                    'last_printing', 'price'])
    def create(name, description, cuisine, copyright_date, last_printing,
               price):
        """Create a new cookbook."""

    featured = Attribute("The currently featured cookbook.")


class IDishSet(IHasGet):
    """The set of all dishes, annotated for export to the web service."""
    export_as_webservice_collection(IDish)

    @collection_default_content()
    def getDishes():
        """Return the list of dishes."""


class IRecipeSet(IHasGet):
    """The set of all recipes, annotated for export to the web service."""
    export_as_webservice_collection(IRecipe)

    @collection_default_content()
    def getRecipes():
        """Return the list of recipes."""

    def removeRecipe(recipe):
        """Remove a recipe from the list."""


class IFileManager(IHasGet):
    """A simple manager for hosted binary files.

    This is just an example for how you might host binary files. It's
    only useful for testing purposes--you'll need to come up with your
    own implementation, or use lazr.librarian.
    """

    def put(name, value):
        """Store a file in the manager."""

    def delete(name):
        """Delete a file from the manager."""


class IFileManagerBackedByteStorage(IByteStorage):

    id = Attribute("The manager ID for this file.")

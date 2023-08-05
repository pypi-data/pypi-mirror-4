
from zope.component import adapts
from zope.interface import implements, Interface
from zope.schema import List, Text

from lazr.restful.example.base.interfaces import IRecipe

from lazr.restful.declarations import (
    export_as_webservice_entry, exported)


class IHasComments(Interface):
    export_as_webservice_entry(contributes_to=[IRecipe])
    comments = exported(
        List(title=u'Comments made by users', value_type=Text()))


class RecipeToHasCommentsAdapter:
    implements(IHasComments)
    adapts(IRecipe)

    def __init__(self, recipe):
        self.recipe = recipe

    @property
    def comments(self):
        return comments_db.get(self.recipe.id, [])


# A fake database for storing comments. Monkey-patch this to test the
# IHasComments adapter.
comments_db = {}

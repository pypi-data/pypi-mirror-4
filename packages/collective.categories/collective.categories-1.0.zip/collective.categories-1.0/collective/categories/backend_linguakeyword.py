from zope import component
from zope import i18nmessageid
from zope import interface
from Products.Archetypes import atapi

from archetypes.schemaextender.field import ExtensionField
from archetypes.linguakeywordwidget import LinguaKeywordWidget

from collective.categories import backend
from Products.Archetypes.interfaces.base import IBaseContent
from collective.categories.backend import DefaultBackend

_ = i18nmessageid.MessageFactory('collective.categories')


class ExtensionCategoriesField(ExtensionField, atapi.LinesField):
    """ Retrofitted date field """


class CategoriesExtender(object):
    """Add Categories field"""

    fields = [
        ExtensionCategoriesField("categories",
            schemata="categorization",
            widget=LinguaKeywordWidget(label=_(u"Categories")),
            )
    ]

    def __init__(self, context):
        self.context = context


class Backend(DefaultBackend):
    interface.implements(backend.ICategoriesBackend)
    component.adapts(IBaseContent)

    def __init__(self, context):
        self.context = context

    def get_extender_class(self):
        """Return the class to use as extender"""
        return CategoriesExtender

    def get_categories(self):
        values = self.indexer()
        language = self.context.Language()
        return [(value, value[len(language) + 1:]) for value in values]

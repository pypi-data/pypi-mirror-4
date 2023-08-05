import logging

from zope import interface, i18nmessageid
from zope import component
from Products.Archetypes import atapi
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.interfaces.base import IBaseContent
from plone.registry.interfaces import IRegistry
from plone.indexer import indexer

_ = i18nmessageid.MessageFactory('collective.categories')
logger = logging.getLogger("collective.categories")


class ICategoriesBackend(interface.Interface):
    """Categorie backend provide the necessary to store and index categories"""

    def get_extender_class():
        """Return the class to use as extender"""

    def get_categories():
        """return categories as key/value pairs"""

    def indexer():
        """return categories for indexing (encoded strings)"""

class ExtensionCategoriesField(ExtensionField, atapi.LinesField):
    """ Retrofitted date field """


class DefaultExtender(object):
    """default extender use keyword"""

    fields = [
        ExtensionCategoriesField("categories",
            schemata="categorization",
            widget=atapi.KeywordWidget(label=_(u"Categories")),
            )
    ]

    def __init__(self, context):
        self.context = context


class DefaultBackend(object):
    """This is the default backend"""
    interface.implements(ICategoriesBackend)
    component.adapts(IBaseContent)

    def __init__(self, context):
        self.context = context

    def get_extender_class(self):
        return DefaultExtender

    def get_categories(self):
        values = self.indexer()
        return [(value, value) for value in values]

    def indexer(self):
        if not hasattr(self.context, 'getField'):
            return []
        field = self.context.getField('categories')
        if not field:
            return []
        values = field.get(self.context)
        return values


def get_backend(context):
    registry = component.queryUtility(IRegistry)
    name = ""
    backend = None
    if registry:
        name = registry.get('collective.categories.backend', 'default')
        backend = component.queryAdapter(context,
                                         interface=ICategoriesBackend,
                                         name=unicode(name))
    if not backend:
        if name:
            logger.error('Could not find %s backend for categories' % name)
        backend = DefaultBackend(context)
    return backend


@indexer(IBaseContent)
def categories_indexer(context):
    backend = get_backend(context)
    return backend.indexer()

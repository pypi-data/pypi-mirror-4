from zope import component
from zope import i18nmessageid
from zope import interface
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName

from Products.ATVocabularyManager import NamedVocabulary
from Products.ATVocabularyManager.utils.vocabs import fetchValuePathFromVDict
from collective.categories.backend import ICategoriesBackend, DefaultBackend
from Products.Archetypes.interfaces.base import IBaseContent

_ = i18nmessageid.MessageFactory('collective.categories')


class ExtensionCategoriesField(ExtensionField, atapi.LinesField):
    """ Retrofitted date field """


class CategoriesExtender(object):
    """Add Categories field"""

    fields = [
        ExtensionCategoriesField("categories",
            schemata="categorization",
            vocabulary=NamedVocabulary('collective_categories'),
            widget=atapi.MultiSelectionWidget(label=_(u"Categories")),
            )
    ]

    def __init__(self, context):
        self.context = context


class Backend(DefaultBackend):
    """ATVocabularyManager based categories backend"""

    def get_extender_class(self):
        return CategoriesExtender

    def get_categories(self):
        categories = []

        field = self.context.getField('categories')
        if not field:
            return
        values = field.get(self.context)
        if not values:
            return
        atvm = getToolByName(self.context, 'portal_vocabularies')
        if not atvm:
            return
        vocab = atvm.getVocabularyByName('collective_categories')
        if not vocab:
            return
        vdict = vocab.getVocabularyDict()

        for uid in values:
            path = fetchValuePathFromVDict(uid, vdict)

            if path:
                cdict = vdict
                for key in path.split('/'):
                    if key:
                        categories.append(cdict[key][0])
                        cdict = cdict[key][1]

        return categories

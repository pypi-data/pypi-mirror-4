from binascii import b2a_qp
from zope import component
from zope import interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode


class CategoriesVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        self.catalog = getToolByName(context, "portal_catalog")

        if self.catalog is None:
            return SimpleVocabulary([])

        index = self.catalog._catalog.getIndex('categories')

        items = [SimpleTerm(i, b2a_qp(i), safe_unicode(i))\
                 for i in index._index]

        return SimpleVocabulary(items)

CategoriesVocabularyFactory = CategoriesVocabulary()


class BackendsVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        backends = list(component.getAdapters((self.context,),
                                              ICategoriesBackend))
        items = []
        for name, backend in backends:
            items.append(SimpleTerm(name, name, unicode(name)))
        return SimpleVocabulary(items)

BackendsVocabularyFactory = BackendsVocabulary()

import transaction
import unittest2 as unittest
from plone.app import testing
from collective.categories import testing as ctesting
from Products.ATVocabularyManager.utils.vocabs import createHierarchicalVocabs


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        pass


class IntegrationTestCase(unittest.TestCase):

    layer = ctesting.INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']

        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Manager'])
        testing.login(self.portal, testing.TEST_USER_NAME)
        atvm = self.portal.portal_vocabularies
        vkey = 'collective_categories'
        vocab = atvm.getVocabularyByName(vkey)

        if not vocab:
            vdict = {(vkey, 'collective.categories'): {}}
            createHierarchicalVocabs(atvm, vdict)
            vocab = atvm.getVocabularyByName(vkey)

        self.portal.invokeFactory('Folder', 'test-folder')
        testing.setRoles(self.portal, testing.TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']


class FunctionalTestCase(IntegrationTestCase):

    layer = ctesting.FUNCTIONAL

    def setUp(self):
        #we must commit the transaction
        transaction.commit()

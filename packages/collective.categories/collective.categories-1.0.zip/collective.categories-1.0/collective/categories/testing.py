from plone.testing import z2
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting, PloneSandboxLayer
#from plone.app.testing import PLONE_FIXTURE


class MyLayer(PloneSandboxLayer):
#    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.categories
        import Products.ATVocabularyManager
        import archetypes.linguakeywordwidget
        self.loadZCML(package=Products.ATVocabularyManager)
        self.loadZCML(package=archetypes.linguakeywordwidget)
        self.loadZCML(package=collective.categories)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'Products.ATVocabularyManager:default')
        self.applyProfile(portal, 'archetypes.linguakeywordwidget:default')
        self.applyProfile(portal, 'collective.categories:default')


FIXTURE = MyLayer()

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                        name="collective.categories:Integration")


FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                        name="collective.categories:Functional")

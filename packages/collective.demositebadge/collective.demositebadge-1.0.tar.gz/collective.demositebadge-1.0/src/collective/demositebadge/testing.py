from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile, quickInstallProduct
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import ploneSite

from plone.testing import z2

from zope.configuration import xmlconfig


class CollectiveDemoSiteBadgeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.demositebadge
        import plone.app.registry
        xmlconfig.file(
            'configure.zcml',
            plone.app.registry,
            context=configurationContext
        )
        xmlconfig.file(
            'configure.zcml',
            collective.demositebadge,
            context=configurationContext
        )
    
    def setUpPloneSite(self, portal):
        quickInstallProduct(portal, 'plone.app.registry')
        quickInstallProduct(portal, 'collective.demositebadge')



COLLECTIVE_DEMOSITEBADGE_FIXTURE = CollectiveDemoSiteBadgeLayer()
COLLECTIVE_DEMOSITEBADGE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_DEMOSITEBADGE_FIXTURE,),
    name="CollectiveDemoSiteBadgeLayer:Integration"
)

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class CollectivedelegatesiteadminLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.delegatesiteadmin
        xmlconfig.file(
            'configure.zcml',
            collective.delegatesiteadmin,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.delegatesiteadmin:default')

COLLECTIVE_DELEGATESITEADMIN_FIXTURE = CollectivedelegatesiteadminLayer()
COLLECTIVE_DELEGATESITEADMIN_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_DELEGATESITEADMIN_FIXTURE,),
    name="CollectivedelegatesiteadminLayer:Integration"
)
COLLECTIVE_DELEGATESITEADMIN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_DELEGATESITEADMIN_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectivedelegatesiteadminLayer:Functional"
)

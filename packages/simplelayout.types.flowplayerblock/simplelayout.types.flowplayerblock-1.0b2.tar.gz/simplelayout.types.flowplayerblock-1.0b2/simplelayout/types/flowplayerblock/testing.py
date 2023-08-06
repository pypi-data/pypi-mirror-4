from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from plone.testing import z2
from zope.configuration import xmlconfig


class SimplelayoutFlowplayerBlock(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import simplelayout.types.flowplayerblock
        import collective.flowplayer
        import simplelayout.base
        import simplelayout.types.common

        xmlconfig.file('configure.zcml', simplelayout.types.flowplayerblock,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', collective.flowplayer,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', simplelayout.base,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', simplelayout.types.common,
                       context=configurationContext)

        # installProduct() is *only* necessary for packages outside
        # the Products.* namespace which are also declared as Zope 2
        # products, using <five:registerPackage /> in ZCML.
        z2.installProduct(app, 'simplelayout.types.flowplayerblock')
        z2.installProduct(app, 'simplelayout.base')
        z2.installProduct(app, 'simplelayout.types.common')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'simplelayout.base:default')
        applyProfile(portal, 'simplelayout.types.common:default')
        applyProfile(portal, 'simplelayout.types.flowplayerblock:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


SL_FLOWPLAYERBLOCK_FIXTURE = SimplelayoutFlowplayerBlock()
SL_FLOWERPLAYERBLOCK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SL_FLOWPLAYERBLOCK_FIXTURE, ), name="SlFlowplayerBlock:Integration")
SL_FLOWERPLAYERBLOCK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SL_FLOWPLAYERBLOCK_FIXTURE, ), name="SlFlowplayerBlock:Functional")

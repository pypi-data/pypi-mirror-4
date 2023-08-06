from Acquisition import aq_parent
from zope.configuration import xmlconfig
from plone.app.testing import (
    PloneSandboxLayer, applyProfile, IntegrationTesting,
    FunctionalTesting, login, logout, layers)
from plone.app.testing.interfaces import (
    SITE_OWNER_NAME,
    TEST_USER_ID)
PLONE_FIXTURE = layers.PloneFixture()


class AddGroupLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpPloneSite(self, portal):
        portal.manage_permission("Manage users",
                roles=['Reviewer', 'Manager'], acquire=True)
        portal.manage_permission("Add Groups",
                roles=['Manager'], acquire=True)
        self.create_folder(portal)

    def setUpZope(self, app, configurationContext):
        import collective.local.addgroup
        xmlconfig.file('configure.zcml', collective.local.addgroup, context=configurationContext)

    def create_folder(self, portal):
        app = aq_parent(portal)
        login(app, SITE_OWNER_NAME)
        portal.invokeFactory('Folder', 'test-folder',
            title="Test Folder")
        folder = portal['test-folder']
        folder.manage_setLocalRoles(TEST_USER_ID, ('Reviewer', ))
        folder.reindexObjectSecurity()
        return folder


MY_PRODUCT_FIXTURE = AddGroupLayer()
MY_PRODUCT_INTEGRATION_TESTING = IntegrationTesting(bases=(MY_PRODUCT_FIXTURE,), name="AddGroupLayer:Integration")
MY_PRODUCT_FUNCTIONAL_TESTING = FunctionalTesting(bases=(MY_PRODUCT_FIXTURE,), name="AddGroupLayer:Functional")

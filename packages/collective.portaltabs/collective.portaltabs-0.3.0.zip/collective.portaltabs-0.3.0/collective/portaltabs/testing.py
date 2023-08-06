# -*- coding: utf-8 -*-

from zope.configuration import xmlconfig

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import applyProfile
from plone.app.testing import TEST_USER_ID

class PortalTabLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.portaltabs
        xmlconfig.file('configure.zcml',
                       collective.portaltabs,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.portaltabs:default')
        portal.acl_users.userFolderAddUser('admin_user', 'secret', ['Member', 'Manager'], [])
        portal.acl_users.userFolderAddUser('sa_user', 'secret', ['Member', 'Site Administrator'], [])


PORTAL_TABS_FIXTURE = PortalTabLayer()
PORTAL_TABS_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(PORTAL_TABS_FIXTURE, ),
                       name="PortalTabs:Integration")
PORTAL_TABS_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(PORTAL_TABS_FIXTURE, ),
                      name="PortalTabs:Functional")


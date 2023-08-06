# -*- coding: utf-8 -*-

from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry

from collective.portaltabs import logger
from collective.portaltabs.interfaces import IPortalTabsSettings
from collective.portaltabs.persistent_field import PortalActionCategory

PROFILE_ID = 'profile-collective.portaltabs:default'

def _moveToPropertySheet(portal):
    # phase 1: copy properties to registry
    logger.info("Copying old property sheet values to registry")
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IPortalTabsSettings, check=False)
    old_properties = portal.portal_properties.portaltabs_settings
    settings.manageable_categories = tuple()
    for p in old_properties.manageable_categories:
        id, title = p.split('|')
        settings.manageable_categories += (PortalActionCategory(id, title.decode('utf-8')),)
        logger.info("...%s copied" % id)
    # phase 2: delete property sheet
    portal.portal_properties.manage_delObjects(['portaltabs_settings'])
    logger.info("Old portaltabs_settings property sheet deleted")

def migrateTo2000(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(PROFILE_ID)
    _moveToPropertySheet(portal)
    logger.info("Migrated to 0.3.0")

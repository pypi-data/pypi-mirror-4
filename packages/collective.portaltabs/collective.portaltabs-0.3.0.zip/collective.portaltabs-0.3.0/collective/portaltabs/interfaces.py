# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema

from collective.portaltabs import messageFactory as _

from collective.portaltabs.persistent_field import IPortalActionCategory
from collective.portaltabs.persistent_field import PersistentObject
from collective.portaltabs.persistent_field import PortalActionCategory

class IPortalTabsLayer(Interface):
    """Marker interface for the collective.portaltabs layer"""


class IPortalTabsSettings(Interface):
    """
    General category settings for collective.portaltabs
    """
    
    manageable_categories = schema.Tuple(
        title=_(u"portal_action categories"),
        description=_('help_manageable_categories',
                      default=u"Users will be able to manage only categories listed there"),
        required=True,
        value_type=PersistentObject(IPortalActionCategory, title=_(u"portal_action category")),
        default=(PortalActionCategory('portal_tabs', u'Portal tabs'),),
        missing_value=(),
    )

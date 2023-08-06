# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface, implements

from z3c.form.object import registerFactoryAdapter

from plone.registry.field import PersistentField

from collective.portaltabs import messageFactory as _

class IPortalActionCategory(Interface):
    category_id = schema.ASCIILine(title=_(u"Category ID"), required=True)
    category_title = schema.TextLine(title=_(u"Title to display"),
                                     description=_('help_category_title',
                                                   default="Will be displayed in the relative control panel fieldset"),
                                     required=True)

class PortalActionCategory(object):
    implements(IPortalActionCategory)

    def __init__(self, category_id=None, category_title=u''):
        self.category_id = category_id
        self.category_title = category_title

class PersistentObject(PersistentField, schema.Object):
    pass

registerFactoryAdapter(IPortalActionCategory, PortalActionCategory)
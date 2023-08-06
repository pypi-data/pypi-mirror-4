# -*- coding: utf-8 -*-

#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel

from z3c.form import button
from z3c.form import group
from z3c.form import field

from collective.portaltabs.interfaces import IPortalTabsSettings
from collective.portaltabs import messageFactory as _

class PortalTabsSettingsControlPanelEditForm(controlpanel.RegistryEditForm):
    """collective.portaltabs settings form.
    """
    schema = IPortalTabsSettings
    id = "PortalTabsSettingsEditForm"
    label = _(u"Portal tabs categories")
    description = _(u"help_action_categories_settings_editform",
                    default=u"Choose which portal categories users will be able to manage")

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")
        self.request.response.redirect("@@manage-portaltabs")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  "@@manage-portaltabs"))


class PortalTabsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """collective.portaltabs settings control panel
    """
    form = PortalTabsSettingsControlPanelEditForm
    #index = ViewPageTemplateFile('controlpanel.pt')

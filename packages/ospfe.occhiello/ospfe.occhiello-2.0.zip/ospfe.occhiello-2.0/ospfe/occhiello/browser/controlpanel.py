# -*- coding: utf-8 -*-

#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from z3c.form import button

from plone.app.registry.browser import controlpanel

from ospfe.occhiello.interfaces import IOcchielloSettings
from ospfe.occhiello import messageFactory as _

class OcchielloSettingsControlPanelEditForm(controlpanel.RegistryEditForm):
    """Occhiello settings form.
    """
    schema = IOcchielloSettings
    id = "OcchielloSettingsEditForm"
    label = _(u"Occhiello settings")
    description = _(u"help_occhiello_settings_editform",
                    default=u"Manage site configuration for half-title field")

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@occhiello-settings")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))


class OcchielloSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """Open Graph settings control panel.
    """
    form = OcchielloSettingsControlPanelEditForm
    #index = ViewPageTemplateFile('controlpanel.pt')

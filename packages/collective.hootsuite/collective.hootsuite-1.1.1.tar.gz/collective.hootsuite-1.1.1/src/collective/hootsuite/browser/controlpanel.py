from plone.app.registry.browser import controlpanel

from collective.hootsuite.interfaces import IHootsuiteRegistry, _
from z3c.form import button
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.hootsuite.interfaces import IHootsuiteRegistry
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.schema.vocabulary import SimpleVocabulary


class HootsuiteSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IHootsuiteRegistry
    label = _(u"Hootsuite settings")
    description = _(u"""""")

    def updateFields(self):
        super(HootsuiteSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(HootsuiteSettingsEditForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@hootsuite-settings")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))


class HootsuiteControlPanel(controlpanel.ControlPanelFormWrapper):
    form = HootsuiteSettingsEditForm
    index = ViewPageTemplateFile('controlpanel_layout.pt')

    def authurl(self):
        """ URL to connect
        """
        return "@@hootsuite-authorize"


    def refreshurl(self):
        """ URL to connect
        """
        return "@@hootsuite-refresh"
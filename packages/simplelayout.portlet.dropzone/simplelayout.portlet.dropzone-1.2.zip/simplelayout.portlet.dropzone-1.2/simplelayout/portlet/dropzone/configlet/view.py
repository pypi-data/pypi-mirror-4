from interfaces import ISimplelayoutConfigurationPortlet
from persistent import Persistent
from plone.app.controlpanel.events import ConfigurationChangedEvent
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.form.validators import null_validator
from plone.fieldsets.fieldsets import FormFieldsets
from plone.protect import CheckAuthenticator
from Products.statusmessages.interfaces import IStatusMessage
from simplelayout.portlet.dropzone import websiteMessageFactory as _
from zope.component import getUtility, getMultiAdapter
from zope.event import notify
from zope.formlib import form
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty


def getPortletConfigUtil(context):
    return getUtility(ISimplelayoutConfigurationPortlet,
                      name='sl-portlet-config')


#we implement plone.app.controlpanel.form.ControlPanelForm
#for a plone look adn feel
class SimpleLayoutConfigurationPortletForm(ControlPanelForm):
    # now we use plone.fieldsets to make a better ui

    PortletSets = FormFieldsets(ISimplelayoutConfigurationPortlet)
    PortletSets.label = _(u'config for blocks in portlet column')
    PortletSets.id = 'portlet_column_sizes'

    label = _(u"Simplelayout Portlet Drop Zone configuration")
    form_name = _(u'Simplelayout Portlet Drop Zone configuration form')
    description = _(u'This form is used to configure the simplelayout')


    form_fields = FormFieldsets(PortletSets)

    @form.action(_(u'label_save'), name=u'save')
    def handle_edit_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
            notify(ConfigurationChangedEvent(self, data))
            self._on_save(data)
        else:
            self.status = _("No changes made.")

    @form.action(_(u'label_cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''

#we have to define a object with the given attributes to store our data
class SimpleLayoutPortletConfiguration(Persistent):
    implements(ISimplelayoutConfigurationPortlet)

    small_size_portlet = FieldProperty(
        ISimplelayoutConfigurationPortlet['small_size_portlet'])
    middle_size_portlet = FieldProperty(
        ISimplelayoutConfigurationPortlet['middle_size_portlet'])
    full_size_portlet = FieldProperty(
        ISimplelayoutConfigurationPortlet['full_size_portlet'])

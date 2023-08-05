# -*- coding: utf-8 -*-

from zope.formlib import form
from zope.interface import implements
from Products.CMFCore.utils import getToolByName

try:
    import plone.app.blob
    BLOB = True
except ImportError:
    BLOB = False

try:
    import Products.contentmigration
    MIGRATION = True
except ImportError:
    MIGRATION = False

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.form import named_template_adapter
from plone.app.controlpanel.form import ControlPanelForm
from plone.protect import CheckAuthenticator
from plone.app.form.validators import null_validator
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter

from redturtle.smartlink.interfaces import ISmartLink
from redturtle.smartlink.interfaces.utility import ISmartlinkConfig
from redturtle.smartlink import smartlinkMessageFactory as _
from redturtle.smartlink.interfaces.utility import ISmartLinkControlPanelForm

class SmartlinkConfigForm(ControlPanelForm):
    """Smartlink Control Panel Form"""
    
    implements(ISmartLinkControlPanelForm)
    template = ViewPageTemplateFile('controlpanel.pt')

    form_fields = form.Fields(ISmartlinkConfig)

    label = _(u"Smart Link configuration")
    description = _(u'setting_description',
                    default=(u'Fill this configuration panel for production settings; '
                             u'choose if use relative paths, an unified front-end URL, or manually '
                             u'enter many back-end/front-end URL (for advanced installation).\n'
                             u'Every configuration option take precedence on the one that follows.\n'
                             u'After changes you (probably) want to run the "Update existing links" task.'))
    form_name = _(u"Settings")

    @property
    def blob_installed(self):
        return BLOB

    @property
    def contentmigration_installed(self):
        return MIGRATION

    def saveFields(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _(u"Changes saved.")
            self._on_save(data)
        else:
            self.status = _(u"No changes made.")

    @form.action(_(u'label_save_links', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        self.saveFields(action, data)

    @form.action(_(u'label_cancel_links', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/@@smartlink-config')
        return ''

    @form.action(_(u'label_update_links', default=u'Update existing links'), name=u'update_links')
    def action_update(self, action, data):
        context = self.context
        putils = getToolByName(context, 'plone_utils')
        results = getToolByName(context, 'portal_catalog')(object_provides=ISmartLink.__identifier__)
        cnt = 0
        for res in results:
            cnt+=1
            object = res.getObject()
            object.setRemoteUrl(object.getRemoteUrl())
            object.reindexObject()
        putils.addPortalMessage(_('update_count_message',
                                  default=u"${count} elements updated",
                                  mapping={'count': cnt}))
        return


# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.formlib import form
try: # >= 4.1
    from five.formlib import formbase
except ImportError: # < 4.1
    from Products.Five.formlib import formbase

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from redturtle.smartlink.migrator import migrateSmartLink, migrateLinkToSmartLink
from redturtle.smartlink import smartlinkMessageFactory as _

try:
    import Products.contentmigration
    MIGRATION_MODULE = True
except ImportError:
    MIGRATION_MODULE = False

class IMigrateBlobsSchema(Interface):
    pass


class MigrateBlobs(formbase.PageForm):
    form_fields = form.FormFields(IMigrateBlobsSchema)
    label = _(u'BLOBs Migration')
    description = _(u'Migrate Smart Link, making it use plone.app.blob')

    @form.action(_(u'Migrate'))
    def actionMigrate(self, action, data):
        if MIGRATION_MODULE:
            messages = migrateSmartLink(self.context)
            i = 0
            for m in messages:
                i+=1
                IStatusMessage(self.request).addStatusMessage(m, type='info')
            portal = getToolByName(self.context, 'portal_url').getPortalObject()
            portal.plone_utils.addPortalMessage(_('sequence_help_message',
                                                  default=u"$num element(s) migrated",
                                                  mapping={'num': i}))

            return self.request.response.redirect(self.context.absolute_url())
        else:
            output = _(u'migration_error_msg',
                       default=u'You need to install "Products.contentmigration" product for perform the task')
            IStatusMessage(self.request).addStatusMessage(output, type='error')
            return self.request.response.redirect(self.context.absolute_url()+'/@@blob-smartlink-migration')
        

    @form.action(_(u'Cancel'))
    def actionCancel(self, action, data):
        return self.request.response.redirect(self.context.absolute_url())


class MigrateToSmartLink(formbase.PageForm):
    form_fields = form.FormFields(IMigrateBlobsSchema)
    label = _(u'Migrate ATLink to Smart Link')
    description = _(u'Migrate basic Plone ATLink to Smart Link')

    @form.action(_(u'Migrate'))
    def actionMigrate(self, action, data):
        output = migrateLinkToSmartLink(self.context)
        cnt = 0
        for l in output:
            cnt+=1
            IStatusMessage(self.request).addStatusMessage(l, type='info')
        IStatusMessage(self.request).addStatusMessage(_('update_count_message',
                                                        default="${count} elements updated", mapping={'count': cnt}),
                                                      type='info')
        return self.request.response.redirect(self.context.absolute_url() + '/@@smartlink-config')

    @form.action(_(u'Cancel'))
    def actionCancel(self, action, data):
        return self.request.response.redirect(self.context.absolute_url() + '/@@smartlink-config')

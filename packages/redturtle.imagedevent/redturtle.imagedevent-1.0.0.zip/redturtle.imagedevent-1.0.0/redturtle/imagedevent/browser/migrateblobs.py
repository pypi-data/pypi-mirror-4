# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.formlib import form
try:
    from Products.Five.formlib import formbase
except ImportError:
    from five.formlib import formbase
from Products.statusmessages.interfaces import IStatusMessage

from redturtle.imagedevent import imagedeventMessageFactory as _
from redturtle.imagedevent.migrator import migrateImagedEvent

class IMigrateBlobsSchema(Interface):
    pass


class MigrateBlobs(formbase.PageForm):
    form_fields = form.FormFields(IMigrateBlobsSchema)
    label = _(u'Blobs Migration')
    description = _(u'Migrate imaged event, making it use plone.app.blob')

    @form.action(_(u'Migrate Event images'))
    def actionMigrate(self, action, data):
        output = migrateImagedEvent(self.context)
        IStatusMessage(self.request).addStatusMessage(output, type='info')
        return self.request.response.redirect(self.context.absolute_url())        

    @form.action(_(u'Cancel'))
    def actionCancel(self, action, data):
        return self.request.response.redirect(self.context.absolute_url())

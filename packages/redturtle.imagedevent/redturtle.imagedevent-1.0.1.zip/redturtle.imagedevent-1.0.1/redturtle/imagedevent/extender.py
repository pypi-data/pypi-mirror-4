# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import AnnotationStorage
from Products.ATContentTypes.configuration import zconf

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from interfaces import IImagedEvent
from redturtle.imagedevent import imagedeventMessageFactory as _

from Products.validation import V_REQUIRED

from plone.app.blob.field import ImageField as BlobImageField


class ExtensionBlobImageField(ExtensionField, BlobImageField):
    """Image Field with blob support that uses sizes defined in plone.app.imaging
    """


class ImageExtender(object):
    adapts(IImagedEvent)
    implements(ISchemaExtender)

    fields = [
        ExtensionBlobImageField('image',
            required = False,
            storage = AnnotationStorage(migrate=True),
            languageIndependent = True,
            max_size = zconf.ATNewsItem.max_image_dimension,
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
            pil_quality = zconf.pil_config.quality,
            pil_resize_algo = zconf.pil_config.resize_algo,
            validators = (('isNonEmptyFile', V_REQUIRED),
                          ('checkNewsImageMaxSize', V_REQUIRED)),
            widget = ImageWidget(
                                 label= _(u'label_imagedevent_image', default=u'Image'),
                                 description = _(u'help_imagedevent_image',
                                                 default=u"Will be shown views that render content's "
                                                         u"images and in the event view itself"),
                                 show_content_type=False,
            ),
        ),

    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


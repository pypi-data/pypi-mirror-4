"""Definition of the Event content type
"""

from zope.interface import implements
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.event import ATEventSchema

from redturtle.imagedevent import imagedeventMessageFactory as _
from Products.ATContentTypes import ATCTMessageFactory as atct_m
from Products.Archetypes import PloneMessageFactory as at_m

from redturtle.imagedevent.interfaces import IImagedEvent
from redturtle.imagedevent.config import PROJECTNAME

from Products.ATContentTypes.configuration import zconf
from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED

from Products.ATContentTypes.permission import ChangeEvents
from types import StringType
from Products.CMFCore import permissions

validation.register(MaxSizeValidator('checkNewsImageMaxSize',
                                     maxsize=zconf.ATNewsItem.max_file_size))

ImagedEventSchema = ATEventSchema.copy() + atapi.Schema((

    # *** from the old ATCT event ***
    atapi.LinesField('eventType',
               required=False,
               searchable=True,
               write_permission = ChangeEvents,
               languageIndependent=True,
               widget = atapi.KeywordWidget(
                        size = 6,
                        description='',
                        label = atct_m(u'label_event_type', default=u'Event Type(s)')
                        )),

    # *** Images field ***
    atapi.ImageField('image',
        required = False,
        storage = atapi.AnnotationStorage(migrate=True),
        languageIndependent = True,
        max_size = zconf.ATNewsItem.max_image_dimension,
        sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },
        validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkNewsImageMaxSize', V_REQUIRED)),
        widget = atapi.ImageWidget(
            label= _(u'label_imagedevent_image', default=u'Image'),
            description = _(u'help_imagedevent_image', default=u"Will be shown views that render content's images and in the event view itself"),
            show_content_type = False)
        ),

    atapi.StringField('imageCaption',
        required = False,
        searchable = True,
        widget = atapi.StringWidget(
            description = '',
            label = _(u'label_image_caption', default=u'Image Caption'),
            size = 40)
        ),

))

ImagedEventSchema['title'].storage = atapi.AnnotationStorage()
ImagedEventSchema['description'].storage = atapi.AnnotationStorage()
ImagedEventSchema['subject'].widget.visible = {'edit': 'visible'}
ImagedEventSchema['subject'].mode = 'wr'
ImagedEventSchema['subject'].widget.label = at_m(u'label_tags', default=u'Tags')

ImagedEventSchema.moveField('eventType', after='attendees')

ImagedEventSchema.moveField('image', after='text')
ImagedEventSchema.moveField('imageCaption', after='image')

schemata.finalizeATCTSchema(ImagedEventSchema, moveDiscussion=False)
# finalizeATCTSchema moves 'location' into 'categories', we move it back:
ImagedEventSchema.changeSchemataForField('location', 'default')
ImagedEventSchema.moveField('location', before='startDate')

class ImagedEvent(ATEvent):
    """Information about an upcoming event, which can be displayed in the calendar."""
    implements(IImagedEvent)

    meta_type = "ATEvent"
    schema = ImagedEventSchema
    
    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'size')
    def size(self):
        """Get size of the image
        """
        return self.get_size()

    security.declareProtected(permissions.View, 'get_size')
    def get_size(self):
        """ZMI / Plone get size method
        """
        f = self.getField('image')
        if f is None:
            return 0
        return f.get_size(self) or 0

    security.declareProtected(permissions.View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            kwargs['title'] = self.getImageCaption()
        return self.getField('image').tag(self, **kwargs)

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return ATEvent.__bobo_traverse__(self, REQUEST, name)

    security.declareProtected(ChangeEvents, 'setEventType')
    def setEventType(self, value, alreadySet=False, **kw):
        """CMF compatibility method

        Changing the event type.
        """
        if type(value) is StringType:
            value = (value,)
        elif not value:
            # mostly harmless?
            value = ()
        f = self.getField('eventType')
        f.set(self, value, **kw) # set is ok

    security.declareProtected(permissions.ModifyPortalContent, 'setSubject')
    def setSubject(self, value, **kw):
        """CMF compatibility method

        Changing the subject.
        """
        f = self.getField('subject')
        f.set(self, value, **kw) # set is ok
    
atapi.registerType(ImagedEvent, PROJECTNAME)

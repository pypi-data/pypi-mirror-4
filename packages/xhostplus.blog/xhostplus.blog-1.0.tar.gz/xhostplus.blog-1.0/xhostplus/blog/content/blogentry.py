"""Definition of the Blog Entry content type
"""

from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

# -*- Message Factory Imported Here -*-
from xhostplus.blog import blogMessageFactory as _
from xhostplus.blog.interfaces import IBlogEntry
from xhostplus.blog.config import PROJECTNAME

BlogEntrySchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.ImageField(
        'title_image',
        required=False,
        sizes={
            'large'   : (768, 768),
            'preview' : (400, 400),
            'mini'    : (200, 200),
            'thumb'   : (128, 128),
            'tile'    :  (64, 64),
            'icon'    :  (32, 32),
            'listing' :  (16, 16),
        },
        widget=atapi.ImageWidget(
            label=_(u"Title Image"),
        ),
        validators=('isNonEmptyFile'),
    ),

    atapi.StringField(
        name='title_image_caption',
        storage=atapi.AnnotationStorage(),
        required=False,
        searchable=True,
        default='',
        widget=atapi.StringWidget(
            label=_(u"Title Image Caption"),
        ),
    ),

    atapi.TextField(
        'text',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.RichWidget(
            label=_(u"Body Text"),
            rows=35,
        ),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

BlogEntrySchema['title'].storage = atapi.AnnotationStorage()
BlogEntrySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(BlogEntrySchema, moveDiscussion=False)


class BlogEntry(base.ATCTContent):
    """A entry in a blog"""
    implements(IBlogEntry)

    meta_type = "BlogEntry"
    schema = BlogEntrySchema
    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            kwargs['title'] = self.title_image_caption
        return self.getField('title_image').tag(self, **kwargs)

    def get_author_portrait(self):
        mtool = getToolByName(self, 'portal_membership')
        portrait = mtool.getPersonalPortrait(id=self.Creator(), verifyPermission=False)
        return portrait

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    title_image_caption = atapi.ATFieldProperty('title_image_caption')

    text = atapi.ATFieldProperty('text')

atapi.registerType(BlogEntry, PROJECTNAME)

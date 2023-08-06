"""Definition of the Blog content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from xhostplus.blog import blogMessageFactory as _
from xhostplus.blog.interfaces import IBlog
from xhostplus.blog.config import PROJECTNAME

BlogSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

BlogSchema['title'].storage = atapi.AnnotationStorage()
BlogSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    BlogSchema,
    folderish=True,
    moveDiscussion=False
)


class Blog(folder.ATFolder):
    """A blog containing blog entries"""
    implements(IBlog)

    meta_type = "Blog"
    schema = BlogSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Blog, PROJECTNAME)

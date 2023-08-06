"""Definition of the MediaPage content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import event
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import StringField
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import StringWidget
from Products.ATContentTypes import ATCTMessageFactory as _

# -*- Message Factory Imported Here -*-

from Products.mediaPage.interfaces import IMediaPage
from Products.mediaPage.config import PROJECTNAME

MediaPageSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MediaPageSchema['title'].storage = atapi.AnnotationStorage()
MediaPageSchema['description'].storage = atapi.AnnotationStorage()
MediaPageSchema['text'].storage = atapi.AnnotationStorage()


schemata.finalizeATCTSchema(
    MediaPageSchema,
    folderish=True,
    moveDiscussion=False
)


class MediaPage(folder.ATFolder):
    """Folderish Page"""
    implements(IMediaPage)

    meta_type = "MediaPage"
    schema = MediaPageSchema
    schema['relatedItems'].widget.visible['edit'] = 'visible'

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(MediaPage, PROJECTNAME)

"""Definition of the Media Event content type
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

from Products.mediaEvent.interfaces import IMediaEvent
from Products.mediaEvent.config import PROJECTNAME

MediaEventSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    DateTimeField('startDate',
        required=False,
        searchable=False,
        accessor='start',
        write_permission = ModifyPortalContent,
        default_method=None,
        languageIndependent=True,
        widget = CalendarWidget(
              description= '',
              label=_(u'label_event_start', default=u'Event Starts'),
              starting_year = 1900
              )),

    DateTimeField('endDate',
        required=False,
        searchable=False,
        accessor='end',
        write_permission = ModifyPortalContent,
        default_method = None,
        languageIndependent=True,
        widget = CalendarWidget(
              description = '',
              label = _(u'label_event_end', default=u'Event Ends'),
              starting_year = 1900
              )),
    
    StringField('location',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = '',
            label = _(u'label_event_location', default=u'Event Location')
            )),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MediaEventSchema['title'].storage = atapi.AnnotationStorage()
MediaEventSchema['description'].storage = atapi.AnnotationStorage() 
MediaEventSchema['text'].storage = atapi.AnnotationStorage()
MediaEventSchema['startDate'].storage = atapi.AnnotationStorage()
MediaEventSchema['endDate'].storage = atapi.AnnotationStorage()
MediaEventSchema['location'].storage = atapi.AnnotationStorage()

MediaEventSchema.moveField('startDate', before='text')
MediaEventSchema.moveField('endDate', before='text')

schemata.finalizeATCTSchema(
    MediaEventSchema,
    folderish=True,
    moveDiscussion=False
)


class MediaEvent(folder.ATFolder):
    """Event type that has a folderish behaviour to store media related to the event."""
    implements(IMediaEvent)

    meta_type = "MediaEvent"
    schema = MediaEventSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')
    startDate = atapi.ATFieldProperty('startDate')
    endDate = atapi.ATFieldProperty('endDate')
    location = atapi.ATFieldProperty('location')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(MediaEvent, PROJECTNAME)

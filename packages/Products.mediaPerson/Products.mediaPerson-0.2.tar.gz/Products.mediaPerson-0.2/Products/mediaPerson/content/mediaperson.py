"""Definition of the Media Person content type
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

from Products.mediaPerson.interfaces import IMediaPerson
from Products.mediaPerson.config import PROJECTNAME

MediaPersonSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy() + atapi.Schema((
    # -*- Your Archetypes field definitions here ... -*-
    DateTimeField('born',
        required=False,
        searchable=False,
        accessor='start',
        write_permission = ModifyPortalContent,
        default_method=None,
        languageIndependent=True,
        widget = CalendarWidget(
              description= '',
              label=_(u'label_event_start', default=u'Born'),
              starting_year = 1900,
              show_hm = False
              )),

    DateTimeField('died',
        required=False,
        searchable=False,
        accessor='end',
        write_permission = ModifyPortalContent,
        default_method = None,
        languageIndependent=True,
        widget = CalendarWidget(
              description = '',
              label = _(u'label_event_end', default=u'Died'),
              starting_year = 1900,
              show_hm = False
              )),

))

# Set storage on fields copied from ATFolderSchema, making sure 
# they work well with the python bridge properties.

MediaPersonSchema['title'].widget.label = _(u'label_name', default=u'Name')
MediaPersonSchema['text'].widget.label = _(u'label_biography', default=u'Biography')

MediaPersonSchema['title'].storage = atapi.AnnotationStorage()
MediaPersonSchema['description'].storage = atapi.AnnotationStorage()
MediaPersonSchema['text'].storage = atapi.AnnotationStorage()
MediaPersonSchema['born'].storage = atapi.AnnotationStorage()
MediaPersonSchema['died'].storage = atapi.AnnotationStorage()

MediaPersonSchema.moveField('born', before='text')
MediaPersonSchema.moveField('died', before='text')

schemata.finalizeATCTSchema(
    MediaPersonSchema,
    folderish=True,
    moveDiscussion=False
)


class MediaPerson(folder.ATFolder):
    """Person with media such as video and images"""
    implements(IMediaPerson)

    meta_type = "MediaPerson"
    schema = MediaPersonSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')
    born = atapi.ATFieldProperty('born')
    died = atapi.ATFieldProperty('died')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(MediaPerson, PROJECTNAME)

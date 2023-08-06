"""Definition of the Media Organization content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import StringField
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import StringWidget
from Products.ATContentTypes import ATCTMessageFactory as _

# -*- Message Factory Imported Here -*-

from Products.mediaOrganization.interfaces import IMediaOrganization
from Products.mediaOrganization.config import PROJECTNAME

MediaOrganizationSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy() + atapi.Schema((

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
              label=_(u'label_start', default=u'Started'),
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
              label = _(u'label_end', default=u'Ended'),
              starting_year = 1900
              )),
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MediaOrganizationSchema['title'].storage = atapi.AnnotationStorage()
MediaOrganizationSchema['description'].storage = atapi.AnnotationStorage()
MediaOrganizationSchema['text'].storage = atapi.AnnotationStorage()
MediaOrganizationSchema['startDate'].storage = atapi.AnnotationStorage()
MediaOrganizationSchema['endDate'].storage = atapi.AnnotationStorage()

MediaOrganizationSchema.moveField('startDate', before='text')
MediaOrganizationSchema.moveField('endDate', before='text')

schemata.finalizeATCTSchema(
    MediaOrganizationSchema,
    folderish=True,
    moveDiscussion=False
)


class MediaOrganization(folder.ATFolder):
    """Organization type with media such as  images and video""" 
    implements(IMediaOrganization)

    meta_type = "MediaOrganization"
    schema = MediaOrganizationSchema
    schema['relatedItems'].widget.visible['edit'] = 'visible'

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')
    startDate = atapi.ATFieldProperty('startDate')
    endDate = atapi.ATFieldProperty('endDate')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(MediaOrganization, PROJECTNAME)

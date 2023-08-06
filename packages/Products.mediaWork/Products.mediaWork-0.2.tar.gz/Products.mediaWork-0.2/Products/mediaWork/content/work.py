"""Definition of the Work content type
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

from Products.mediaWork.interfaces import IWork
from Products.mediaWork.config import PROJECTNAME

WorkSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    DateTimeField('date',
        required=False,
        searchable=False,
        accessor='date',
        write_permission = ModifyPortalContent,
        default_method=None,
        languageIndependent=True,
        widget = CalendarWidget(
              description= '',
              label=_(u'label_date', default=u'Date'),
              starting_year = 1900
              )),
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

WorkSchema['title'].storage = atapi.AnnotationStorage()
WorkSchema['description'].storage = atapi.AnnotationStorage()
WorkSchema['text'].storage = atapi.AnnotationStorage()
WorkSchema['date'].storage = atapi.AnnotationStorage()

WorkSchema.moveField('date', before='text')

schemata.finalizeATCTSchema(
    WorkSchema,
    folderish=True,
    moveDiscussion=False
)


class Work(folder.ATFolder):
    """Work"""
    implements(IWork)

    meta_type = "Work"
    schema = WorkSchema
    schema['relatedItems'].widget.visible['edit'] = 'visible'

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')
    date = atapi.ATFieldProperty('date')
    

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Work, PROJECTNAME)

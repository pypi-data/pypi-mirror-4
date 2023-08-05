"""Definition of the SPSpeakersFolder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
# from Products.ATContentTypes.content import folder
from Products.Archetypes.atapi import OrderedBaseFolder
# from Products.ATContentTypes.content import schemata

from slc.seminarportal.interfaces import ISpeakersFolder
from slc.seminarportal.config import PROJECTNAME

SPSpeakersFolderSchema = atapi.OrderedBaseFolderSchema.copy()

# SPSpeakersFolderSchema['title'].storage = atapi.AnnotationStorage()
# SPSpeakersFolderSchema['description'].storage = atapi.AnnotationStorage()

# schemata.finalizeATCTSchema(SPSpeakersFolderSchema, folderish=True,
# moveDiscussion=False)


class SPSpeakersFolder(OrderedBaseFolder):
    """Folder containing Seminar Speakers"""
    implements(ISpeakersFolder)

    portal_type = "SPSpeakersFolder"
    schema = SPSpeakersFolderSchema

    # title = atapi.ATFieldProperty('title')
    # description = atapi.ATFieldProperty('description')

atapi.registerType(SPSpeakersFolder, PROJECTNAME)

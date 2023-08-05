"""Definition of the SPSpeechVenueFolder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from slc.seminarportal.interfaces import ISpeechVenueFolder
from slc.seminarportal.config import PROJECTNAME

SPSpeechVenueFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

SPSpeechVenueFolderSchema['title'].storage = atapi.AnnotationStorage()
SPSpeechVenueFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SPSpeechVenueFolderSchema, folderish=True,
                            moveDiscussion=False)


class SPSpeechVenueFolder(folder.ATFolder):
    """Folder containing Speech Venues"""
    implements(ISpeechVenueFolder)

    portal_type = "SPSpeechVenueFolder"
    schema = SPSpeechVenueFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(SPSpeechVenueFolder, PROJECTNAME)

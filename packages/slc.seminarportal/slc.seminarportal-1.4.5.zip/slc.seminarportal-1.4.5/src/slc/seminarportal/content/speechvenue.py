from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder

from slc.seminarportal.config import PROJECTNAME
from slc.seminarportal.interfaces import ISpeechVenue

SPSpeechVenueSchema = folder.ATFolderSchema.copy()
SPSpeechVenueSchema['title'].widget.label = 'Venue Name'
SPSpeechVenueSchema['description'].widget.label = 'Venue Description'
SPSpeechVenueSchema['description'].widget.description = \
    'Please provide a brief introduction or description of this venue.'


class SPSpeechVenue(folder.ATFolder):
    """ Represents a venue, hall or room where speeches are held during
        a seminar.
    """
    implements(ISpeechVenue)
    meta_type = portal_type = "SPSpeechVenue"

    _at_rename_after_creation = True

    def get_path(self):
        return '/'.join(self.getPhysicalPath())


atapi.registerType(SPSpeechVenue, PROJECTNAME)

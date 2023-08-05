from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from slc.seminarportal.content.speakersfolder import SPSpeakersFolder
from slc.seminarportal.content.speechvenuefolder import SPSpeechVenueFolder
from slc.seminarportal.interfaces import ISeminar

ADDITIONAL_TYPES_INFO = (
    ('speakers', 'Speakers', SPSpeakersFolder),
    ('speech-venues', 'Speech Venues', SPSpeechVenueFolder)
)


class SeminarEvents:
    """ Event Subscriber for the SPSeminar object type """

    def __call__(self, obj, event, **kw):
        """ Called by the event system """
        if ISeminar.providedBy(obj):
            if IObjectInitializedEvent.providedBy(event):
                self.objectInitialized(obj, **kw)

    def objectInitialized(self, seminar, **kw):
        """ Create Speakers and Speeches folder inside the seminar after
            creation.
        """
        for fid, title, type in ADDITIONAL_TYPES_INFO:

            if shasattr(seminar, fid):
                continue

            seminar._setObject(fid, type(fid))
            folder = getattr(seminar, fid)
            folder.setTitle(title)
            folder.setExcludeFromNav(1)


event_subscriber = SeminarEvents()


def handle_workflowChanged(object, event):
    """ make sure the additional folders of the seminar have the same WF state
    as the seminar itself"""
    transition = event.transition
    if transition:
        wftool = getToolByName(object, 'portal_workflow')

        for fid, title, type in ADDITIONAL_TYPES_INFO:
            folder = getattr(object, fid, None)
            if not folder:
                continue
            try:
                wftool.doActionFor(folder, transition.id)
            except WorkflowException:
                pass

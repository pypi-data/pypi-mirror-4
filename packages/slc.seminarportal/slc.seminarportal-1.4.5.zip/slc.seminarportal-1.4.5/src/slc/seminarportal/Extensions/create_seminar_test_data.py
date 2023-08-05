import logging
import random

from zope import event

from DateTime import DateTime

from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from slc.seminarportal.config import names
from slc.seminarportal.config import titles
from slc.seminarportal.config import short_desc
from slc.seminarportal.config import desc
from slc.seminarportal.config import conclusions

from slc.seminarportal.utils import create_speaker
from slc.seminarportal.utils import create_speech

log = logging.getLogger('create_seminar_test_data.py')

FOLDER_ID = 'seminars-test'


def run(self):
    create_test_seminars(self, 5)


def create_test_seminars(
                    self,
                    count,
                    create_speakers=True,
                    create_speeches=True,
                    past=False):

    wftool = getToolByName(self, 'portal_workflow')
    sf = create_seminar_folder(self)
    parent = getParent(self)
    sf = getattr(parent, FOLDER_ID)
    for i in range(0, count):
        seminar_day = DateTime() + 10
        t = titles[i % len(titles)]
        sid = self.generateUniqueId('SPSeminar')
        seminar = create_seminar(self, sf, sid, t, desc, conclusions, past)
        speakers_folder = getattr(seminar, 'speakers')

        if create_speakers:
            log.info('Creating Speakers')
            for surname, firstname in names:
                speaker = create_speaker(
                                    speakers_folder,
                                    surname,
                                    firstname
                                    )

        speakers = speakers_folder.objectValues()
        num_of_speakers = len(speakers)

    if not create_speeches:
        return

    speech_venues_folder = getattr(seminar, 'speech-venues')
    for i in ['A', 'B']:
        log.info('Creating venue: %s' % i)
        speech_folder_id = 'speech_venue_%s' % i.lower()
        speech_venues_folder.invokeFactory(
                                    'SPSpeechVenue',
                                    speech_folder_id,
                                    title='Speech Venue %s' % i,
                                    description=short_desc,
                                    )

        speech_folder = getattr(speech_venues_folder, speech_folder_id)
        wftool.doActionFor(speech_folder, 'publish')
        for days in [0, 1, 2]:
            for title in titles:
                speech_title = 'Speech: %s' % title
                start_hour = random.randint(6, 20)
                end_hour = start_hour + random.randint(0, 3)
                start_date = DateTime(
                    '%s %s:%s ' % ((seminar_day + days).Date(),
                                   start_hour, random.randint(0, 30)))
                end_date = DateTime(
                    '%s %s:%s' % ((seminar_day + days).Date(),
                                  end_hour, random.randint(30, 59)))

                speech = create_speech(
                                    speech_folder,
                                    speech_title,
                                    desc,
                                    start_date,
                                    end_date
                                    )

                if speakers:
                    speech_speakers = []
                    for i in range(0, 2):
                        rand_index = random.randint(0, num_of_speakers - 1)
                        speaker = speakers[rand_index]
                        speech_speakers.append(speaker)
                    speech.setSpeakers(speech_speakers)
                    speech.reindexObject()

    return 'Finished'


def getParent(self):
    """ Helper method to enable me to quickly change seminar parent
        folder, for now it's the site root.
    """
    portal = getToolByName(self, 'portal_url').getPortalObject()
    return portal


def create_seminar_folder(self):
    parent = getParent(self)
    if not hasattr(parent, FOLDER_ID):
        parent.invokeFactory(
            'Folder', FOLDER_ID, title='Seminars TEST',
            description='Folder containing a collection of Seminars')

    seminar_folder = getattr(parent, FOLDER_ID)
    wftool = getToolByName(self, 'portal_workflow')
    try:
        wftool.doActionFor(seminar_folder, 'publish')
    except WorkflowException:
        log.error("Could not publish the 'Seminars' folder")

    return seminar_folder


def create_seminar(self, parent, seminar_id, title, desc, conclusions, past):
    if not hasattr(parent, seminar_id):
        subject = random.sample(['cat1', 'cat2', 'cat3'], 1)[0]
        if past:
            end_date = DateTime() - random.randint(1, 10)
            start_date = end_date - random.randint(1, 4)
        else:
            start_date = DateTime() + random.randint(0, 10)
            end_date = start_date + random.randint(1, 4)

        parent.invokeFactory('SPSeminar',
                             seminar_id,
                             title=title,
                             description=desc,
                             conclusions=conclusions,
                             )
        s = getattr(parent, seminar_id)
        s._renameAfterCreation(check_auto_id=True)
        s.setStartDate(start_date)
        s.setEndDate(end_date)
        s.setSubject(subject)
        s.reindexObject()
        event.notify(ObjectInitializedEvent(s))

        wftool = getToolByName(self, 'portal_workflow')
        wftool.doActionFor(s, 'publish')
        return s

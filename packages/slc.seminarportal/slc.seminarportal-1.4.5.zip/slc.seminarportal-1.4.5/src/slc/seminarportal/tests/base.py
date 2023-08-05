import logging
import random
import unittest2 as unittest

from DateTime import DateTime

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.browserlayer import utils as browserlayerutils
from plone.testing import z2
from Products.CMFCore.utils import getToolByName

from slc.seminarportal.config import names
from slc.seminarportal.config import titles
from slc.seminarportal.config import desc
from slc.seminarportal.config import short_desc
from slc.seminarportal.utils import create_speech
from slc.seminarportal.interfaces import IThemeLayer

log = logging.getLogger('tests/base.py')


class SlcSeminarPortal(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import slc.seminarportal
        self.loadZCML('configure.zcml', package=slc.seminarportal)
        import Products.LinguaPlone
        self.loadZCML('configure.zcml', package=Products.LinguaPlone)
        import Products.Relations
        self.loadZCML('configure.zcml', package=Products.Relations)

        z2.installProduct(app, 'slc.seminarportal')
        z2.installProduct(app, 'Products.Relations')
        z2.installProduct(app, 'Products.LinguaPlone')

    def setUpPloneSite(self, portal):
        # Needed to get the workflows
        applyProfile(portal, 'Products.CMFPlone:plone')

        applyProfile(portal, 'slc.seminarportal:default')

        # Login as manager and create a test folder
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'folder')

        browserlayerutils.register_layer(
            IThemeLayer,
            name="slc.seminarportal.browserlayer"
        )

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'slc.seminarportal')
        z2.uninstallProduct(app, 'Products.Relations')
        z2.uninstallProduct(app, 'Products.LinguaPlone')


SLC_SEMINARPORTAL_FIXTURE = SlcSeminarPortal()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(SLC_SEMINARPORTAL_FIXTURE,),
    name="SlcSeminarPortal:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SLC_SEMINARPORTAL_FIXTURE,),
    name="SlcSeminarPortal:Functional")


class SeminarPortalTestCase(unittest.TestCase):
    """Base class used for test cases
    """

    layer = INTEGRATION_TESTING

    def create_speakers(self, seminar):
        """ Create test speakers
        """
        speakers_folder = getattr(seminar, 'speakers')
        for surname, firstname in names:
            speaker_id = seminar.generateUniqueId('SPSpeaker')
            speakers_folder.invokeFactory('SPSpeaker', speaker_id)
            s = getattr(speakers_folder, speaker_id)
            s._renameAfterCreation(check_auto_id=True)
            s.setLastName(surname)
            s.setFirstName(firstname)

    def create_speech_venues(self, seminar):
        """ """
        wftool = getToolByName(seminar, 'portal_workflow')
        speech_venues_folder = getattr(seminar, 'speech-venues')
        for i in ['A', 'B']:
            log.info('Creating venue: %s' % i)
            speech_folder_id = 'speech_venue_%s' % i.lower()
            speech_venues_folder.invokeFactory(
                'SPSpeechVenue',
                speech_folder_id,
                title='Speech Venue %s' % i,
                description=short_desc
            )

            speech_folder = getattr(speech_venues_folder, speech_folder_id)
            wftool.doActionFor(speech_folder, 'publish')

    def create_speeches(self, seminar):
        """ """
        speech_venues = getattr(seminar, 'speech-venues').objectValues()
        speakers = getattr(seminar, 'speakers').objectValues()
        seminar_day = DateTime() + 10
        for venue in speech_venues:
            for days in [0, 1, 2]:
                for title in titles:
                    speech_title = 'Speech: %s' % title
                    start_hour = random.randint(6, 20)
                    end_hour = start_hour + random.randint(0, 3)
                    start_date = DateTime('%s %s:%s ' % (
                        (seminar_day + days).Date(),
                        start_hour,
                        random.randint(0, 30))
                    )
                    end_date = DateTime('%s %s:%s' % (
                        (seminar_day + days).Date(),
                        end_hour,
                        random.randint(30, 59))
                    )
                    speech = create_speech(
                        venue, speech_title, desc, start_date, end_date)
                    speech_speakers = []
                    for i in range(0, 2):
                        rand_index = random.randint(0, len(speakers) - 1)
                        speaker = speakers[rand_index]
                        speech_speakers.append(speaker)
                    speech.setSpeakers(speech_speakers)
                    speech.reindexObject()

import logging
import unittest2 as unittest

from zope import event

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.utils import shasattr

from slc.seminarportal.tests.base import SeminarPortalTestCase

log = logging.getLogger('test_seminar.py')


class TestSeminar(SeminarPortalTestCase):

    def setUp(self):
        """ Create a Seminar object, and call the relevant event to enable the
            auto-creation of the sub-objects ('speakers', 'speech venues').
        """
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.portal.invokeFactory('SPSeminar', 'plone-conference',
                                   title="Seminar")
        seminar = getattr(self.portal, 'plone-conference')
        seminar._renameAfterCreation(check_auto_id=True)
        event.notify(ObjectInitializedEvent(seminar))
        self.seminar = seminar

    def test_subfolders_created(self):
        """ Test for the succesful automatic creation of subfolders.
        """
        seminar = getattr(self.portal, 'plone-conference')

        # Check that subflolders are created.
        self.failUnlessEqual(shasattr(seminar, 'speakers'), True)
        self.failUnlessEqual(shasattr(seminar, 'speech-venues'), True)


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class(es) above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

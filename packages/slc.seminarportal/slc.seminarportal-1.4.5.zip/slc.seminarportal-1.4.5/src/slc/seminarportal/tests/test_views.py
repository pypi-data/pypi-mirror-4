import logging
from DateTime import DateTime
import unittest2 as unittest

from zope.interface import directlyProvides

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from slc.seminarportal.tests.base import SeminarPortalTestCase
from slc.seminarportal.Extensions.create_seminar_test_data import  \
                                                    create_test_seminars

from slc.seminarportal.interfaces import IThemeLayer
log = logging.getLogger('test_views.py')


class TestViews(SeminarPortalTestCase):

    def setUp(self):
        """ Create a Seminar object, and call the relevant event to enable the
            auto-creation of the sub-objects ('speakers', 'speech venues').
        """
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_querying(self):
        """ """
        directlyProvides(self.portal.REQUEST, IThemeLayer)

        views = self.portal.restrictedTraverse('@@seminars-view')
        create_test_seminars(self.portal, 5, False, past=True)
        seminars = views.seminars()

        self.assertEquals(len(seminars), 5)

        now = DateTime()
        for seminar in seminars:
            self.assertEquals(seminar.end < now, True)

        create_test_seminars(self.portal, 5, False, past=True)
        seminars = views.seminars()
        self.assertEquals(len(seminars), 10)

        for seminar in seminars:
            self.assertEquals(seminar.end < now, True)


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class(es) above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

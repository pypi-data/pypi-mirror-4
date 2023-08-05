import logging
import random
import unittest2 as unittest

from zope import event
from zope import component

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from Products.Archetypes.event import ObjectInitializedEvent

from slc.seminarportal.tests.base import SeminarPortalTestCase
from slc.seminarportal.portlets import speeches as speeches_portlet

log = logging.getLogger('test_speeches_portlet.py')

class TestPortlet(SeminarPortalTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_portlet_registered(self):
        portlet = component.getUtility(IPortletType,
                                       name="slc.SpeechesPortlet")
        self.assertEquals(portlet.addview, "slc.SpeechesPortlet")

    def test_portlet_interfaces(self):
        portlet = speeches_portlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_addview(self):
        portlet = component.getUtility(IPortletType,
                                       name='slc.SpeechesPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   speeches_portlet.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = speeches_portlet.Assignment()
        editview = component.getMultiAdapter((mapping['foo'], request),
                                             name='edit')
        self.failUnless(isinstance(editview, speeches_portlet.EditForm))

    def test_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')

        manager = component.getUtility(
            IPortletManager,
            name='plone.rightcolumn',
            context=self.portal
        )

        assignment = speeches_portlet.Assignment()

        renderer = component.getMultiAdapter(
            (context, request, view, manager, assignment),
            IPortletRenderer
        )

        self.failUnless(isinstance(renderer, speeches_portlet.Renderer))


class TestRenderer(SeminarPortalTestCase):

    def setUp(self):
        """ Create a Seminar object, and call the relevant event to enable the
            auto-creation of the sub-objects ('speakers', 'speech venues').
        """
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        #qi = portal.portal_quickinstaller
        self.portal.invokeFactory('SPSeminar', 'plone-conference',
                                  title="Seminar")
        seminar = getattr(self.portal, 'plone-conference')
        seminar._renameAfterCreation(check_auto_id=True)
        event.notify(ObjectInitializedEvent(seminar))
        self.create_speakers(seminar)
        self.create_speech_venues(seminar)
        self.create_speeches(seminar)
        self.seminar = seminar

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or component.getUtility(
            IPortletManager,
            name='plone.rightcolumn',
            context=self.portal)
        assignment = assignment or speeches_portlet.Assignment()
        return component.getMultiAdapter((context, request, view, manager,
                                          assignment),
                                         IPortletRenderer)

    def test_get_speeches(self):
        """ """
        speech_venues_folder = getattr(self.seminar, 'speech-venues')
        speeches = speech_venues_folder.objectValues()
        #speeches_urls = ['/'.join(s.getPhysicalPath()) for s in speeches]

        # Test random:
        for count in random.sample(range(0, 10), 5):
            assignment = speeches_portlet.Assignment(count=count)

            r = self.renderer(
                context=self.portal,
                assignment=assignment,
            )

            speeches = r.results()

            self.assertEquals(len(speeches), count)
            for speech in speeches:
                self.assertEquals(speech.portal_type, 'SPSpeech')

            #speeches_paths = ['/'.join(s.getPhysicalPath()) for s in speeches]
            # for s in speeches_paths:
            #     self.assertEquals(s in speeches_urls, True)


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class(es) above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

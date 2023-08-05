import logging
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
from slc.seminarportal.portlets import speaker as speaker_portlet

log = logging.getLogger('test_speaker_portlet.py')


class TestPortlet(SeminarPortalTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_portlet_registered(self):
        portlet = component.getUtility(IPortletType, name="slc.SpeakerPortlet")
        self.assertEquals(portlet.addview, "slc.SpeakerPortlet")

    def test_portlet_interfaces(self):
        portlet = speaker_portlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_addview(self):
        portlet = component.getUtility(IPortletType, name='slc.SpeakerPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   speaker_portlet.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = speaker_portlet.Assignment()
        editview = component.getMultiAdapter((mapping['foo'], request),
                                             name='edit')
        self.failUnless(isinstance(editview, speaker_portlet.EditForm))

    def test_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')

        manager = component.getUtility(
                                IPortletManager,
                                name='plone.rightcolumn',
                                context=self.portal
                                )

        assignment = speaker_portlet.Assignment()

        renderer = component.getMultiAdapter(
                                (context, request, view, manager, assignment),
                                IPortletRenderer
                                )

        self.failUnless(isinstance(renderer, speaker_portlet.Renderer))


class TestRenderer(SeminarPortalTestCase):

    def setUp(self):
        """ Create a Seminar object, and call the relevant event to enable the
            auto-creation of the sub-objects ('speakers', 'speech venues').
        """
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        # qi = self.portal.portal_quickinstaller
        self.portal.invokeFactory('SPSeminar', 'plone-conference',
                                  title="Seminar")
        seminar = getattr(self.portal, 'plone-conference')
        seminar._renameAfterCreation(check_auto_id=True)
        event.notify(ObjectInitializedEvent(seminar))
        self.create_speakers(seminar)
        self.seminar = seminar

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or component.getUtility(IPortletManager,
                                        name='plone.rightcolumn',
                                        context=self.portal)
        assignment = assignment or speaker_portlet.Assignment()
        return component.getMultiAdapter((context, request, view, manager,
                                          assignment),
                                         IPortletRenderer)

    def test_get_speakers(self):
        """ """
        speakers = self.seminar.speakers.objectValues()
        speakers_urls = ['/'.join(s.getPhysicalPath()) for s in speakers]

        # Test random:
        for count in range(0, 10):
            assignment = speaker_portlet.Assignment(
                                                featured_speakers=[],
                                                count=count,
                                                random=1,
                                                )

            r = self.renderer(
                        context=self.portal,
                        assignment=assignment,
                        )

            speakers = r.get_speakers()
            self.assertEquals(len(speakers), count)

            for speaker in speakers:
                self.assertEquals(speaker.portal_type, 'SPSpeaker')

            speakers_paths = ['/'.join(s.getPhysicalPath()) for s in speakers]
            for s in speakers_paths:
                self.assertEquals(s in speakers_urls, True)

        # Test with specified:
        count = 5
        assignment = speaker_portlet.Assignment(
            featured_speakers=speakers_urls[:5],
            count=count,
            random=0,
        )

        r = self.renderer(
                    context=self.portal,
                    assignment=assignment,
                    )

        speakers = r.get_speakers()
        # The speakers
        speakers_paths = ['/'.join(s.getPhysicalPath()) for s in speakers]

        self.assertEquals(len(speakers), count)

        for s in speakers_paths:
            self.assertEquals(s in speakers_urls, True)


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class(es) above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

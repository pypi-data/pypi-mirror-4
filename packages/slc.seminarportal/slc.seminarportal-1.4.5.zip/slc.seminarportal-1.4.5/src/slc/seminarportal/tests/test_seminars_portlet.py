import logging
import unittest2 as unittest

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

from slc.seminarportal.tests.base import SeminarPortalTestCase
from slc.seminarportal.portlets import seminars as seminars_portlet
from slc.seminarportal.Extensions.create_seminar_test_data import  \
                                                    create_test_seminars

log = logging.getLogger('test_seminars_portlet.py')


class TestPortlet(SeminarPortalTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_portlet_registered(self):
        portlet = component.getUtility(IPortletType,
                                       name="slc.SeminarsPortlet")
        self.assertEquals(portlet.addview, "slc.SeminarsPortlet")

    def test_portlet_interfaces(self):
        portlet = seminars_portlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_addview(self):
        portlet = component.getUtility(IPortletType,
                                       name='slc.SeminarsPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={
            'count': 5,
            'state': ('published', ),
            'subject': ('category1', 'category2'),
            'header': 'Testing Seminars Portlet',
        })
        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   seminars_portlet.Assignment))
        assignment = mapping.values()[0]
        self.assertEquals(assignment.count, 5)
        self.assertEquals(assignment.state, ('published',))
        self.assertEquals(assignment.subject, ('category1', 'category2'))
        self.assertEquals(assignment.header, 'Testing Seminars Portlet')

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = seminars_portlet.Assignment()
        editview = component.getMultiAdapter((mapping['foo'], request),
                                             name='edit')
        self.failUnless(isinstance(editview, seminars_portlet.EditForm))

    def test_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')

        manager = component.getUtility(
                                IPortletManager,
                                name='plone.rightcolumn',
                                context=self.portal
                                )

        assignment = seminars_portlet.Assignment()

        renderer = component.getMultiAdapter(
                                (context, request, view, manager, assignment),
                                IPortletRenderer
                                )

        self.failUnless(isinstance(renderer, seminars_portlet.Renderer))


class TestRenderer(SeminarPortalTestCase):

    def setUp(self):
        """ Create a Seminar object, and call the relevant event to enable the
            auto-creation of the sub-objects ('speakers', 'speech venues').
        """
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        """ """
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or component.getUtility(IPortletManager,
                                        name='plone.rightcolumn',
                                        context=self.portal)
        assignment = assignment or seminars_portlet.Assignment()
        return component.getMultiAdapter(
                                (context, request, view, manager, assignment),
                                IPortletRenderer)

    def test_portlet(self):
        """ """
        total_seminars = 10
        seminars = self.portal.objectValues('SPSeminar')
        # seminars_urls = ['/'.join(s.getPhysicalPath()) for s in seminars]

        assignment = seminars_portlet.Assignment(**{
            'count': 5,
            'state': ('published', ),
            'header': 'Testing Seminars Portlet',
        })

        r = self.renderer(
                    context=self.portal,
                    assignment=assignment,
                    )

        # Test that no seminars exist yet and that the portlet will not be
        # available because of it.
        seminars = r._data()
        self.assertEquals(len(seminars), 0)
        self.assertEquals(r.available, False)

        # Create test data.
        create_test_seminars(self.portal, total_seminars, False, False)

        # Test that the portlet returns the correct amount of seminars
        seminars = r._data()
        self.assertEquals(len(seminars), 5)

        # Test that it's actually Seminars being returned.
        for seminar in seminars:
            self.assertEquals(seminar.portal_type, 'SPSeminar')

        # Test with diffferent count values:
        for count in range(0, 12):
            assignment = seminars_portlet.Assignment(**{
                'count': count,
                'state': ('published', ),
                'subject': (),
                'header': 'Testing Seminars Portlet',
            })
            r = self.renderer(
                        context=self.portal,
                        assignment=assignment,
                        )
            seminars = r._data()
            self.assertEquals(len(seminars), count > total_seminars
                              and total_seminars or count)

            if count == 0:
                self.assertEquals(r.available, False)
            else:
                self.assertEquals(r.available, True)

        # Test that subject filtering works:
        for cat in ['cat1', 'cat2', 'cat3']:
            assignment = seminars_portlet.Assignment(**{
                'count': count,
                'state': ('published', ),
                'subject': (cat,),
                'header': 'Testing Seminars Portlet',
            })
            r = self.renderer(
                        context=self.portal,
                        assignment=assignment,
                        )
            seminars = r._data()
            for seminar in seminars:
                self.assertEquals(seminar.Subject, (cat,))


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class(es) above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

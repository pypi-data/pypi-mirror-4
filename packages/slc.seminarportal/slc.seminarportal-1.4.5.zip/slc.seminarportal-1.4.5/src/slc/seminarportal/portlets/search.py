from Acquisition import aq_inner
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.instance import memoize
from plone.memoize.compress import xhtml_compress

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.seminarportal.portlets.base import BaseRenderer
from interfaces import ISearchPortlet


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()


class Assignment(base.Assignment):
    implements(ISearchPortlet)

    @property
    def title(self):
        return u"Search for Seminars, Speakers of Speeches"


class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('search.pt')

    def _render_cachekey(method, self):
        """ Renders a cachekey to be used by the portlets.
        """
        preflang = getToolByName(
            self.context, 'portal_languages').getPreferredLanguage()
        return (preflang, self.navigation_root_path)

    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @memoize
    def here_url(self):
        context = aq_inner(self.context)
        return '/'.join(context.getPhysicalPath())

    @memoize
    def template_id(self):
        return '@@seminar-search'

    def results(self):
        return self._data()

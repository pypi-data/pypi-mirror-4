from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from interfaces import ISpeechesPortlet
from slc.seminarportal.portlets.base import BaseRenderer


class AddForm(base.AddForm):
    form_fields = form.Fields(ISpeechesPortlet)

    label = u"Add a Speeches Portlet"

    def create(self, data):
        return Assignment(count=data.get('count'),)


class EditForm(base.EditForm):
    form_fields = form.Fields(ISpeechesPortlet)
    label = u"Edit the Speeches Portlet"


class Assignment(base.Assignment):
    implements(ISpeechesPortlet)

    def __init__(self, count=None):
        self.count = count

    @property
    def title(self):
        return u"Featured Speeches"


class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('speeches.pt')

    def _render_cachekey(method, self):
        """ Renders a cachekey to be used by the portlets.
        """
        preflang = getToolByName(
            self.context, 'portal_languages').getPreferredLanguage()
        return (preflang, self.navigation_root_path)

    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    def results(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        try:
            count = self.data.count
        except AttributeError:
            count = 5
        if count > 0:
            return catalog(
                portal_type='SPSpeech',
                sort_limit=count,
                sort_on='modified',
                sort_order='reverse')[:count]
        else:
            return []

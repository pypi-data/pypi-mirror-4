import logging
import random
import Acquisition
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.Portal import PloneSite

from slc.seminarportal.portlets.base import BaseRenderer
from interfaces import ISpeakerPortlet

log = logging.getLogger('slc.seminarportal/portlets/speaker.py')


class AddForm(base.AddForm):
    form_fields = form.Fields(ISpeakerPortlet)
    label = u"Add a Speaker Portlet"

    def create(self, data):
        return Assignment(featured_speakers=data.get('featured_speakers'),
                          count=data.get('count'),
                          random=data.get('random'),
                          local=data.get('local'),
                          )


class EditForm(base.EditForm):
    form_fields = form.Fields(ISpeakerPortlet)
    label = u"Edit the Speaker Portlet"


class Assignment(base.Assignment):
    implements(ISpeakerPortlet)

    def __init__(self, featured_speakers=None, count=5, random=True,
        local=False):
        self.featured_speakers = featured_speakers
        self.count = count
        self.random = random
        self.local = local

    @property
    def title(self):
        return u"Featured Speakers"


class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('speaker.pt')

    def _render_cachekey(method, self):
        """ Renders a cachekey to be used by the portlets.
        """
        preflang = getToolByName(self.context,
            'portal_languages').getPreferredLanguage()
        path = '/'.join(self.context.getPhysicalPath())
        return (preflang, path)

    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.get_speakers() and True or False

    def get_speakers(self):
        """ Return the speaker objects as configured by the portlet.
        """
        data = self.data
        if data.local:
            seminar = self.get_current_seminar()
            if seminar:
                catalog = getToolByName(self.context, 'portal_catalog')
                brains = catalog(portal_type='SPSpeech', Language='all',
                    path="/".join(seminar.getPhysicalPath()))

                speeches = [x.getObject() for x in brains]
                speakers = []
                for speech in speeches:
                    ss = speech.getSpeakers()
                    if type(ss) in [list, tuple]:
                        speakers += ss
                    else:
                        speakers.append(ss)

                # eliminate duplicates
                speakers = list(set(speakers))
                if len(speakers) < data.count:
                    speakers.sort(lambda x, y:
                        cmp(x.getLastName(), y.getLastName()))
                    return speakers
                else:
                    random_indexes = random.sample(range(0,
                        len(speakers)), data.count)
                    return [speakers[i] for i in random_indexes]

        elif data.random:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog(portal_type='SPSpeaker')
            limit = len(brains) < data.count and len(brains) or data.count
            random_indexes = random.sample(range(0, len(brains)), limit)
            return [brains[i].getObject() for i in random_indexes]

        elif len(data.featured_speakers) > data.count:
            featured_speakers = []
            for i in random.sample(range(0,
                len(data.featured_speakers)), data.count):
                try:
                    featured_speakers.append(
                            self.portal.unrestrictedTraverse(
                                                    data.featured_speakers[i]))
                except AttributeError:
                    log.warn('Could not find speaker: %s' %
                        data.featured_speakers[i])
                    self.data.featured_speakers.remove(data. \
                        featured_speakers[i])

            return featured_speakers

        elif data.featured_speakers:
            featured_speakers = []
            for speaker in data.featured_speakers:
                try:
                    featured_speakers.append(self.portal. \
                        unrestrictedTraverse(speaker))
                except AttributeError:
                    log.warn('Could not find speaker: %s' % speaker)
                    self.data.featured_speakers.remove(speaker)
            return featured_speakers

        return []

    def get_current_seminar(self):
        """ Return the object of a particular type which is
            the parent of the current object.
        """
        obj = Acquisition.aq_inner(self.context)
        while not isinstance(obj, PloneSite):
            if obj.meta_type == 'SPSeminar':
                return obj
            obj = Acquisition.aq_parent(obj)
        return None

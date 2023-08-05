from zope.interface import implements

import Acquisition
from DateTime import DateTime

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.seminarportal import is_osha_installed
from interfaces import ISeminarView
from interfaces import ISeminarFolderView


class BaseView(BrowserView):
    """" """

    def isAnonymous(self):
        """ """
        anonymous = getToolByName(self, 'portal_membership').isAnonymousUser()
        return anonymous

    def date(self, date=None):
        """Return the DateTime obj
        """
        return DateTime(date)

    def get_countries_dict(self):
        """Return the values from the index
        """
        cutils = getToolByName(self.context, 'portal_countryutils')
        return cutils.getCountryIsoDict()

    def increment_date(self, date):
        return DateTime(date) + 1

    def cropHtmlText(self, text, length, ellipsis='...'):
        """ First strip html, then crop """
        context = Acquisition.aq_inner(self.context)
        portal_transforms = getToolByName(context, 'portal_transforms')
        text = portal_transforms.convert('html_to_text', text).getData()
        return context.restrictedTraverse('@@plone').cropText(
            text, length, ellipsis)

    def seminars(self):
        """ Return brains for SPSeminar objects in context
        """
        context = Acquisition.aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        if not IFolderish.providedBy(context):
            # We might be on a index_html
            folder = context.aq_parent
        else:
            folder = self.context

        query = {
            'portal_type': 'SPSeminar',
            'path': '/'.join(folder.getPhysicalPath()),
            'sort_on': 'start',
            'sort_order': 'reverse',
            }
        return catalog(query)

    def search(self):
        """ Return brains for all the seminar related objects
        """
        request = self.request
        if not 'SearchableText' in request:
            return []
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'portal_type': ['SPSeminar',
                            'SPSpeech',
                            'SPSpeaker',
                            'SPSpeechVenue']
        }

        if request.get('st') == 'spl':
            # simple search
            searchable_text = request.get('SearchableText', '')
            query['SearchableText'] = searchable_text
            if not searchable_text:
                query['sort_on'] = 'start'
                query['sort_order'] = 'reverse'
            brains = catalog(query)

        if request.get('st') == 'adv':
            # advanced search
            date = request.get('date')
            if date:
                query['end'] = {'query': date, 'range': 'min'}
                query['start'] = {'query': date.replace('00:00', '23:59'),
                                  'range': 'max'}

            location = request.get('location')
            if location:
                query['location'] = location

        brains = catalog(query)
        return list(brains)


class SeminarFolderView(BaseView):
    """ View methods for the seminar folder view
    """
    implements(ISeminarFolderView)

    def template_id(self):
        return '@@seminars-view'


class Search(BaseView):
    """ Simple and advanced search functionality for slc.seminar
    """

    def template_id(self):
        return '@@seminar-search'


class SeminarView(BaseView):
    """ Helper functionality for displaying a roster of speeches at a
        Seminar.
    """
    implements(ISeminarView)

    def get_venues(self):
        """ Return brains for SpeechVenue objects in context
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type='SPSpeechVenue',
                         path='/'.join(self.context.getPhysicalPath()),
                         sort_on='getObjPositionInParent',)
        return list(brains)

    def get_roster(self, venues=[]):
        """ Return a dict of {date:{venue_id:{time:[speeches]}}}
        """
        d = {}
        catalog = getToolByName(self.context, 'portal_catalog')
        venues = venues or self.get_venues()
        for venue in venues:
            venue_id = venue.id
            speeches = catalog(
                portal_type='SPSpeech',
                path='%s/speech-venues/%s' % ('/'.join(
                    self.context.getPhysicalPath()), venue_id))
            for speech in speeches:
                date = speech.start.Date()
                time = speech.start
                if date in d:
                    if venue_id in d[date]:
                        if time in  d[date][venue_id]:
                            d[date][venue_id][time].append(speech)
                        else:
                            d[date][venue_id][time] = [speech]
                    else:
                        d[date][venue_id] = {time: [speech]}
                else:
                    d[date] = {venue_id: {time: [speech]}}
        return d

    def get_event_summary(self, venues=[]):
        """ Return a dict of {date:[(time, speech)]}
        """
        d = {}
        catalog = getToolByName(self.context, 'portal_catalog')
        venues = venues or self.get_venues()
        for venue in venues:
            speeches = catalog(
                portal_type='SPSpeech',
                path='%s/speech-venues/%s' % ('/'.join(
                    self.context.getPhysicalPath()), venue.id))
            for speech in speeches:
                date = speech.start.Date()
                time = speech.start
                if date in d:
                    d[date].append((time, speech.getPath(), speech))
                else:
                    d[date] = [(time, speech.getPath(), speech)]
        return d

    def get_day_times(self, roster={}):
        """ Return a dictionary of {seminar_day_date:[speech_time]}
        """
        roster = roster or self.get_roster()
        day_times = {}
        for day in roster.keys():
            d = {}  # Dict used to enforece uniqueness
            for venue_id in roster[day].keys():
                for t in roster[day][venue_id].keys():
                    d[t] = 'dummy'

            day_times[day] = sorted(d.keys())
        return day_times

    def get_files_and_images(self):
        """ Return a list of files and images in current context
        """
        context = Acquisition.aq_inner(self.context)
        objs = context.objectValues(['ATFile', 'ATBlob', 'ATImage'])
        # If there are no attachments and the object is a translation,
        # look on the canonical
        if len(objs) == 0 and not context.isCanonical():
            canonical = context.getCanonical()
            objs = canonical.objectValues(['ATFile', 'ATBlob', 'ATImage'])
        objs = [(o.pretty_title_or_id(), o) for o in objs]

        return objs

    def get_speechvenues(self):
        """ Return speech venues in current context
        """
        return self.context.objectValues(['SPSpeechVenue'])

    def query_items(self, type, b_size=10):
        """ """
        context = Acquisition.aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        speeches = catalog(
                    portal_type=type,
                    path='/'.join(context.getPhysicalPath())
                    )

        b_start = self.request.get('b_start', 0)
        batch = Batch(speeches, b_size, int(b_start), orphan=0)
        return batch


class SpeakerView(SeminarView):
    """ Override speech view so that we can hook our check for eliminating
        translations of speeches
    """
    template = ViewPageTemplateFile('templates/speaker_view.pt')

    def __call__(self, *args, **kw):
        if is_osha_installed:
            obj = self.context
            speeches = obj.getSpeeches()
            valid = list(set([x.getCanonical().UID() for x in speeches]))
            obj.setSpeeches(valid)

        return self.template()

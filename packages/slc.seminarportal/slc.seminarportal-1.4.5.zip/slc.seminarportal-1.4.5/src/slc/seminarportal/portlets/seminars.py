from Acquisition import aq_inner

from zope import schema
from zope.interface import implements
from zope.formlib import form
from zope.i18n import translate

from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Products.Archetypes.utils import shasattr
from Products.ATContentTypes.interface import folder
from Products.ATContentTypes.interface import document
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from slc.seminarportal import _
from slc.seminarportal import is_osha_installed
from slc.seminarportal.portlets.base import BaseRenderer

if is_osha_installed:
    default_header = _(u"Our Events")
    categories_vocabulary = "osha.policy.vocabularies.categories"
    domain = "osha"
else:
    default_header = _(u"Seminars")
    categories_vocabulary = "slc.seminarportal.vocabularies.categories"
    domain = "plone"


class ISeminarsPortlet(IPortletDataProvider):
    """ """
    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        default=default_header,
        required=True
    )
    count = schema.Int(
        title=_(u'Number of Seminars to display'),
        required=True,
        default=5
    )
    state = schema.Tuple(
        title=_(u"Workflow state"),
        description=_(
            u"You may limit the displayed Seminars to a "
            u"specific workflow state.."),
        default=('published', ),
        required=True,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates")
    )
    subject = schema.Tuple(
        title=_(u"Categories"),
        description=_(
            u"Pick one or more categories with which you want to filter "
            u"Seminars."),
        default=tuple(),
        required=False,
        value_type=schema.Choice(
            vocabulary=categories_vocabulary)
    )
    seminarsfolder = schema.Choice(
        title=_(u'Seminars link'),
        description=_(
            u"Choose a folder which the portlet title and "
            u"'Upcoming Seminars' link will point to. This is optional."
        ),
        required=False,
        source=SearchableTextSourceBinder(
            {'object_provides': [
                folder.IATFolder.__identifier__,
                folder.IATBTreeFolder.__identifier__,
                document.IATDocument.__identifier__,
            ]},
            default_query='path:'),
    )


class Renderer(BaseRenderer):
    """ """
    _template = ViewPageTemplateFile('seminars.pt')

    def _render_cachekey(method, self):
        portal_languages = getToolByName(self.context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()
        subject = self.data.subject
        navigation_root_path = self.navigation_root_path
        return (preflang, subject, navigation_root_path)

    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def title(self):
        portal_languages = getToolByName(self.context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()
        return translate(msgid=self.data.header, domain=domain,
            target_language=preflang, context=self.context)

    @property
    def available(self):
        """ The portlet will not appear if there aren't any seminars
        to display.
        """
        return len(self.seminars()) > 0

    @memoize
    def seminars(self):
        return self._data()

    def _data(self):
        """ Get all SPSeminar objects that conform to the workflow state and
            category specified on the portlet.
        """
        if self.data.count == 0:
            return []

        context = aq_inner(self.context)
        # search in the navigation root of the currently selected language
        paths = [self.navigation_root_path]
        if self.navigation_root:
            # Also search in its canonical
            if shasattr(self.navigation_root, 'getCanonical'):
                canonical = self.navigation_root.getCanonical()
                if canonical is not None:
                    paths.append('/'.join(canonical.getPhysicalPath()))

        # Search: Language = preferredLanguage or neutral
        preflang = getToolByName(
            context, 'portal_languages').getPreferredLanguage()
        query = dict(
                    Language=['', preflang],
                    path=paths,
                    portal_type='SPSeminar',
                    review_state=self.data.state,
                    sort_limit=self.data.count,
                    limit=self.data.count,
                    sort_on='start',
                    sort_order='reverse',
                    )

        if self.data.subject:
            if type(self.data.subject) in [str, unicode]:
                query.update(Subject=(self.data.subject,))
            else:
                query.update(Subject=self.data.subject)

        catalog = getToolByName(context, 'portal_catalog')
        return catalog(query)

    @memoize
    def upcoming_seminars_link(self):
        folder_link = getattr(self.data, 'seminarsfolder', None)
        if folder_link:
            return '%s/seminars-view' % folder_link

        return '%s/seminars-view' % self.context.absolute_url()

    @memoize
    def prev_seminars_link(self):
        folder_link = getattr(self.data, 'seminarsfolder', None)
        if folder_link:
            return '%s/seminars-view?past=1' % folder_link

        return '%s/seminars-view?past=1' % self.context.absolute_url()


class Assignment(base.Assignment):
    implements(ISeminarsPortlet)

    def __init__(
                self,
                count=5,
                state=('published', ),
                subject=tuple(),
                header=default_header,
                seminarsfolder=None):

        self.count = count
        self.state = state
        self.subject = subject
        self.header = header
        self.seminarsfolder = seminarsfolder

    @property
    def title(self):
        return self.header


class AddForm(base.AddForm):
    form_fields = form.Fields(ISeminarsPortlet)
    label = _(u"Adding the Seminars Portlet")
    description = _(u"This portlet lists upcoming Seminars.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ISeminarsPortlet)
    label = _(u"Editing the Seminars Portlet")
    description = _(u"This portlet lists upcoming Seminars.")

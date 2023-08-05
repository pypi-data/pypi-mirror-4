from Acquisition import aq_base
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.event import ATEventSchema
from Products.LinguaPlone.I18NBaseObject import AlreadyTranslated
from Products.LinguaPlone.I18NBaseFolder import I18NBaseFolder
from Products.LinguaPlone import permissions

from slc.seminarportal.interfaces import ISeminar
from slc.seminarportal.config import PROJECTNAME, ALLOWABLE_TEXT_TYPES
from slc.seminarportal import seminarportalMessageFactory as _


SeminarSchema = atapi.BaseFolderSchema.copy() + \
    ATEventSchema.copy() + atapi.Schema((

    atapi.ImageField(
        name='logo',
        widget=atapi.ImageWidget(
            label=_(u"label_seminar_logo",
                    default=u"Graphic or Logo for the event"),
        ),
        languageIndependent=True,
        original_size=(200, 200),
        sizes={'thumb': (100, 125), 'normal': (200, 200)},
        default_output_type='image/jpeg',
        allowable_content_types=('image/gif', 'image/jpeg', 'image/png'),
    ),
    atapi.TextField(
        name='summary',
        allowable_content_types=ALLOWABLE_TEXT_TYPES,
        widget=atapi.RichWidget(
            label=_(u"label_seminar_summary",
                    default=u"General Description/Summary of the event"),
            macro='seminar_textarea',
        ),
        default_output_type="text/x-html-safe",
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
    ),
    atapi.TextField(
        name='conclusions',
        allowable_content_types=ALLOWABLE_TEXT_TYPES,
        widget=atapi.RichWidget(
            label=_(u"label_seminar_conclusions",
                    default=u"General Conclusions"),
            macro='seminar_textarea',
        ),
        default_output_type="text/x-html-safe",
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
    ),
    atapi.TextField(
        name='furtherActions',
        allowable_content_types=ALLOWABLE_TEXT_TYPES,
        widget=atapi.RichWidget(
            label=_(u"label_seminar_further_actions",
                    default=u"Further Actions"),
            macro='seminar_textarea',
        ),
        default_output_type="text/x-html-safe",
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
    ),
    atapi.BooleanField(
        name='showRosterHour',
        widget=atapi.BooleanWidget(
            label=_(u"label_seminar_show_hour_column",
                    default=u"Show the hour column in the speech roster?"),
        ),
        languageIndependent=True,
    ),
))

del SeminarSchema['text']

# Change labels and descriptions
SeminarSchema['description'].widget.label = \
    _(u'label_abstract', default=u'Abstract')
SeminarSchema['description'].widget.description = \
    'A short abstract, introduction or description of the event'

SeminarSchema['contactName'].schemata = 'Organiser'
SeminarSchema['contactName'].widget.label = \
    _(u'label_seminar_organiser', default='Organiser')
SeminarSchema['contactName'].widget.description = \
        "Please provide the name of the event organiser."

SeminarSchema['contactEmail'].schemata = 'Organiser'
SeminarSchema['contactPhone'].schemata = 'Organiser'

SeminarSchema['eventUrl'].schemata = 'Organiser'
SeminarSchema['eventUrl'].widget.label = \
    _(u'label_seminar_website', default='Website')
SeminarSchema.moveField('eventUrl', after='contactName')

SeminarSchema['location'].widget = atapi.TextAreaWidget(label='Location')
SeminarSchema['location'].searchable = True

schemata.finalizeATCTSchema(SeminarSchema)

# finalizeATCTSchema moves 'location' into 'categories', we move it back:
SeminarSchema.changeSchemataForField('location', 'default')
SeminarSchema.moveField('location', after='description')
SeminarSchema['startDate'].widget.format = '%A %d %B %Y %H:%M'
SeminarSchema['endDate'].widget.format = '%A %d %B %Y %H:%M'


class SPSeminar(I18NBaseFolder, ATEvent):
    """Description of the Example Type"""
    security = ClassSecurityInfo()
    implements(ISeminar)
    meta_type = portal_type = "SPSeminar"
    schema = SeminarSchema

    _at_rename_after_creation = True

    def seminar_title(self):
        return self.Title()

    def get_path(self):
        return '/'.join(self.getPhysicalPath())

    def get_seminar_start_date(self):
        return self.startDate

    def get_seminar_end_date(self):
        return self.endDate

    security.declareProtected(permissions.ModifyPortalContent, 'setLanguage')
    def setLanguage(self, value, **kwargs):
        """ For some crazy reason, setLanguage failed with an
            AlreadyTranslated error.

            This bug occurs in LinguaPlone 2.2, and is fixed in 2.3

            The code that fails is Products/LinguaPlone/I18NBaseObject.py:332

            Here is a pdb trace showing the problem:
            (Pdb) p self
                <SPSeminar at /osha/Members/admin/test-seminar-nl>
            (Pdb) p self
                <SPSeminar at /osha/Members/admin/test-seminar-nl>
            (Pdb) p translation
                <SPSeminar at /osha/Members/admin/test-seminar-nl>
            (Pdb) self.UID()
                '2000b779359475adf1cd599ab3d5f96f'
            (Pdb) translation.UID()
                '2000b779359475adf1cd599ab3d5f96f'
            (Pdb) self ==  translation
                False
            (Pdb) type(self)
                <type 'ImplicitAcquirerWrapper'>
            (Pdb) type(translation)
                <type 'ImplicitAcquirerWrapper'>
            (Pdb) aq_inner(self) == aq_inner(translation)
                False
            (Pdb) aq_base(self) == aq_base(translation)
                True

            We override the if statement here and use aq_base to fix the
            problem and if necessary then call the original setLanguage
            method.
        """
        translation = self.getTranslation(value)
        if self.hasTranslation(value):
            if aq_base(translation) == aq_base(self):
                return
            else:
                raise AlreadyTranslated, translation.absolute_url()

        super(SPSeminar, self).setLanguage(value)


atapi.registerType(SPSeminar, PROJECTNAME)

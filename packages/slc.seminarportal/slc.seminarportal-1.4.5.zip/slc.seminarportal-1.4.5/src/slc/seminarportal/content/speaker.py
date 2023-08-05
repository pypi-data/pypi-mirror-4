from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.Archetypes.atapi import OrderedBaseFolder
# from Products.LinguaPlone.I18NOrderedBaseFolder import I18NOrderedBaseFolder
from Products.Relations.field import RelationField

from slc.seminarportal.config import PROJECTNAME
from slc.seminarportal.interfaces import ISpeaker
from slc.seminarportal.permissions import ASSIGN_SPEAKERS_TO_SPEECHES
from slc.seminarportal import seminarportalMessageFactory as _


SpeakerSchema = atapi.OrderedBaseFolderSchema.copy() + atapi.Schema((
    atapi.StringField(
        name='firstName',
        widget=atapi.StringWidget(
            label=_(u"label_spaker_first_name", default=u"First Name"),
        ),
        required=True,
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='middleName',
        widget=atapi.StringWidget(
            label=_(u"label_speaker_middle_name", default=u"Middle Name"),
        ),
        required=False,
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='lastName',
        widget=atapi.StringWidget(
            label=_(u"label_speaker_last_name", default=u"Last Name"),
        ),
        required=True,
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='suffix',
        widget=atapi.StringWidget(
            label=_(u"label_speaker_suffix", default=u"Suffix"),
            description=_(u"description_speaker_suffix",
                default=u"Academic, professional, honorary, and social "
                        u"suffixes."),
        ),
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='email',
        user_property=True,
        widget=atapi.StringWidget(
            label=_(u"label_speaker_email", default=u'Email'),
        ),
        schemata="default",
        searchable=True,
        validators=('isEmail',)
    ),
    atapi.LinesField(
        name='jobTitles',
        widget=atapi.LinesField._properties['widget'](
            label=_(u"label_speaker_job_titles", default=u"Job titles"),
            description=_(u"description_speaker_job_titles",
                          default=u"One entry per line"),
        ),
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='officeAddress',
        widget=atapi.TextAreaWidget(
            label=_(u"label_speaker_office_address",
                    default=u"Office address"),
        ),
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='officeCity',
        widget=atapi.StringWidget(
            label=_(u"label_speaker_office_city", default=u"Office city"),
        ),
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='officeState',
        widget=atapi.StringWidget(
            label=_(u"label_speaker_office_state", default=u"Office state"),
        ),
        schemata="default"
    ),
    atapi.StringField(
        name='officePostalCode',
        widget=atapi.StringWidget(
            label=_(u"label_speaker_office_postal_code",
                    default=u"Office postal code"),
        ),
        schemata="default"
    ),
    atapi.StringField(
        name='officePhone',
        widget=atapi.StringWidget(
            label=_(u"label_speaker_office_phone", default=u"Office phone"),
        ),
        schemata="default",
        searchable=True,
    ),
    atapi.ImageField(
        name='image',
        schemata="default",
        widget=atapi.ImageWidget(
            label=_(u"label_speaker_image", default=u'Image'),
            default_content_type='image/gif',
            macro="seminarportal_image",
        ),
        original_size=(100, 125),
        sizes={'small': (50, 50), 'thumb': (75, 75), 'normal': (200, 250)},
        default_output_type='image/jpeg',
        allowable_content_types=('image/gif', 'image/jpeg', 'image/png'),
    ),
    atapi.TextField(
        name='biography',
        widget=atapi.RichWidget(
            label=_(u"label_speaker_biography", default=u'Biography'),
        ),
        schemata="default",
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        user_property='description'
    ),
    atapi.LinesField(
        name='education',
        widget=atapi.LinesField._properties['widget'](
            label=_(u"label_speaker_education", default=u'Education'),
        ),
        schemata="default",
        searchable=True
    ),
    atapi.StringField(
        name='website',
        widget=atapi.LinesField._properties['widget'](
            label=_(u"label_speaker_web_sites", default=u"Web sites"),
        ),
        schemata="default",
    ),
    RelationField(
        name='speeches',
        widget=ReferenceBrowserWidget(
            label=_(u"label_speaker_speeches", default=u'Speeches'),
            description=_(u"description_speaker_speeches",
                          default=u'Any speeches that this person '\
            'held or contributed to, can be added here. Please note that ' \
            'speeches have to be created separately and for the seminar '\
            'at which they were held.'),
            base_query={'portal_type': 'SPSpeech',
                        'sort_on': 'sortable_title'},
            allow_browse=1,
            allow_search=1,
            show_results_without_query=1,
            image_portal_types=('SPSpeech',),
            image_method='bullet.gif',
        ),
        write_permission=ASSIGN_SPEAKERS_TO_SPEECHES,
        allowed_types=('Speech'),
        multiValued=1,
        relationship='speaker_speeches'
    ),
    atapi.StringField(
        name='nationality',
        widget=atapi.StringWidget(
            label=_(u"label_speaker_nationality", default=u"Nationality"),
        ),
    ),
    atapi.StringField(
        name='employer',
        widget=atapi.StringWidget(
            label=_(u"label_speaker_employer", default=u"Employer"),
        ),
    ),
    atapi.StringField(
        name='socialPartnerGroup',
        widget=atapi.StringWidget(
            name=_(u"label_speaker_social_partner_group",
                   default=u"Social Partner Group"),
        ),
    ),
    atapi.TextField(
        name='expertise',
        widget=atapi.TextAreaWidget(
            name=_(u"label_speaker_expertise", default=u"Expertise"),
        ),
    ),
))

SpeakerSchema['title'].widget.label = 'Full Name'
SpeakerSchema['title'].widget.visible = {
    'edit': 'invisible',
    'view': 'visible'
}
SpeakerSchema['description'].widget.label = _(
    u'seo_description_label',
    default=u'SEO Description'
)
SpeakerSchema['description'].widget.description = _(
    u'seo_description_description',
    default= \
    u"Provide here a description that is purely for SEO "
    "(Search Engine Optimisation) purposes. It will "
    "appear in the <meta> tag in the "
    "<head> section of the HTML document, but nowhere "
    "in the actual website content."
)


class SPSpeaker(OrderedBaseFolder):
    """ Speakers are people who hold speeches at seminars
    """
    implements(ISpeaker)
    meta_type = portal_type = "SPSpeaker"
    schema = SpeakerSchema
    security = ClassSecurityInfo()
    _at_rename_after_creation = True

    security.declareProtected(permissions.View, 'Title')
    def Title(self):
        """Return the Title as firstName middleName(when available) lastName,
        suffix(when available)"""
        try:
            # Get the fields using the accessors, so they're properly Unicode
            # encoded. We also can't use the %s method of string concatentation
            # for the same reason.
            # Is there another way to manage this?
            fn = self.getFirstName()
            ln = self.getLastName()
        except AttributeError:
            # YTF doesn't this display on the New Person
            # page? Couldn't call superclass's Title() for some unknown reason
            return u"new person"

        if self.getMiddleName():
            mn = " " + self.getMiddleName() + " "
        else:
            mn = " "

        t = fn + mn + ln
        if self.getSuffix():
            t = t + ", " + self.getSuffix()
        return t

    security.declareProtected(permissions.View, 'getSortableName')
    def getSortableName(self):
        """Return a tuple of the person's name. For sorting purposes return
        them as lowercase so that names like 'von Whatever' sort properly.
        """
        return (self.lastName.lower(), self.firstName.lower())

    def get_path(self):
        return '/'.join(self.getPhysicalPath())


atapi.registerType(SPSpeaker, PROJECTNAME)

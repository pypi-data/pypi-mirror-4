from zope.i18nmessageid import MessageFactory

from Products.Archetypes import atapi
from Products.CMFCore.utils import ContentInit
from Products.CMFCore import DirectoryView

from slc.seminarportal import config

# See http://do3cc.blogspot.com/2010/08/dont-catch-import-errors-use.html
# If osha.policy gets imported here it monkeypatches MembershipTool
# which breaks Products.PlonePAS and causes the tests to fail
import pkg_resources
try:
    pkg_resources.get_distribution('osha.policy')
except pkg_resources.DistributionNotFound:
    is_osha_installed = False
else:
    is_osha_installed = True

DirectoryView.registerDirectory('skins', config.product_globals)

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

seminarportalMessageFactory = MessageFactory('slc.seminarportal')
_ = seminarportalMessageFactory

# adding the days of the week here so that i18n extract will pick them up
monday = _(u'Monday', default=u'Monday')
tuesday = _(u'Tuesday', default=u'Tuesday')
wednesday = _(u'Wednesday', default=u'Wednesday')
thursday = _(u'Thursday', default=u'Thursday')
friday = _(u'Friday', default=u'Friday')
saturday = _(u'Saturday', default=u'Saturday')
sunday = _(u'Sunday', default=u'Sunday')


def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    # Retrieve the content types that have been registered with Archetypes
    # This happens when the content type is imported and the registerType()
    # call in the content type's module is invoked. Actually, this happens
    # during ZCML processing, but we do it here again to be explicit. Of
    # course, even if we import the module several times, it is only run
    # once.

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    # Now initialize all these content types. The initialization process takes
    # care of registering low-level Zope 2 factories, including the relevant
    # add-permission. These are listed in config.py. We use different
    # permissions for each content type to allow maximum flexibility of who
    # can add which content types, where. The roles are set up in rolemap.xml
    # in the GenericSetup profile.

    for atype, constructor in zip(content_types, constructors):
        ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types=(atype,),
            permission=config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors=(constructor,),
            ).initialize(context)

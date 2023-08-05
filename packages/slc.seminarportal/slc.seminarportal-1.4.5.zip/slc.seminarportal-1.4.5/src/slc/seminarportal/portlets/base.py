from zope.component import getMultiAdapter
from plone.app.portlets.portlets import base


class BaseRenderer(base.Renderer):

    def __init__(self, *args):
        super(BaseRenderer, self).__init__(*args)

        #portal_languages = getToolByName(self.context, 'portal_languages')
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')

        self.portal = portal_state.portal()
        self.navigation_root_path = portal_state.navigation_root_path()
        self.navigation_root = self.portal.restrictedTraverse(
            self.navigation_root_path)
        self.navigation_root_url = portal_state.navigation_root_url()

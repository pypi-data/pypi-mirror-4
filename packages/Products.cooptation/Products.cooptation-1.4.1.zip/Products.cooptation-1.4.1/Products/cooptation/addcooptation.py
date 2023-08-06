from Acquisition import aq_inner
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from zope.publisher.browser import BrowserPage


class AddCooptation(BrowserPage):

    def checkAccess(self):
        if not self.request.AUTHENTICATED_USER.has_role(
                ('Manager', 'Reviewer'), object=self.context):
            raise Unauthorized

    def __call__(self):
        self.checkAccess()
        context = aq_inner(self.context)
        uid = context.generateUniqueId(type_name="Cooptation")
        portal_url = getToolByName(context, 'portal_url')()
        role = self.request.get('role', None)
        params = []
        searchstring =  self.request.get('searchstring', None)
#        groupname = self.request.get('groupname', None)
        params.append("workspace=%s" % context.UID())
        if role:
            params.append("role=%s" % role)
        if searchstring:
            params.append("title=%s" % searchstring)
        url = "%s/portal_cooptations/portal_factory/Cooptation/%s/edit?%s" % (
                portal_url,
                uid,
                "&".join(params))
        self.request.response.redirect(url)
        return u""

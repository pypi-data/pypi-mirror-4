from zope.i18n import translate
from zope.i18nmessageid import MessageFactory

from five import grok

from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import (
    IAboveContent, IAboveContentBody)
from Products.CMFCore.utils import getToolByName

from Products.cooptation.content.interfaces import ICooptation

_ = MessageFactory("cooptation")
PMF = MessageFactory("plone")


class GoBackCooptationViewlet(grok.Viewlet):
    grok.name('cooptation.goback')
    grok.context(ICooptation)
    grok.view(IViewView)
    grok.viewletmanager(IAboveContent)

    def render(self):
        label = _(u"label_back", default=u"Back")
        workspace = self.context.getWorkspace()
        if workspace is None:
            return u""
        return (u"""<div style='text-align: right;' class='goback'>"""
                u"""<input type='button' onclick='window.location.href = "%s";'"""
                u""" value='%s' /></div>""") % (
                    workspace.absolute_url(),
                    translate(label, context=self.request),)


class InfoViewlet(grok.Viewlet):
    grok.name("cooptation.info")
    grok.context(ICooptation)
    grok.viewletmanager(IAboveContentBody)

    def render(self):
        if self.context.isTemporary():
            role = self.request.get('role', None)
            uid = self.request.get('workspace', None)
            if uid is None:
                workspace = None
            else:
                reference_catalog = getToolByName(self.context, 'reference_catalog')
                workspace = reference_catalog.lookupObject(uid)
        else:
            role = self.context.getRole()
            workspace = self.context.getWorkspace()
        if not workspace or not role:
            return u""
        role = translate(PMF(role), context=self.request)
        workspace_url =u"""<a href="%s">%s</a>""" % (workspace.absolute_url(), workspace.Title())
        label = _(u"This user will have the role ${role} assigned on the following workspace: ${workspace_url}",
                  mapping={'role': role,
                           'workspace_url': workspace_url})
        return (u"""<p>%s</p>""") % (
                    translate(label, context=self.request),)

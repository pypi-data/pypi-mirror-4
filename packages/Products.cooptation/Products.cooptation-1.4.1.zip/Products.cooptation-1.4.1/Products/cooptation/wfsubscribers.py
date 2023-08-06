# -*- coding: utf-8 -*-
#
# File: wfsubscribers.py
#
# Copyright (c) 2011 by Ecreall
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Vincent Fretin and Michael Launay <development@ecreall.com>"""
__docformat__ = 'plaintext'


##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section module-header


def notifyCooptationPending(obj, event):
    """generated workflow subscriber."""
    # do only change the code section inside this function.
    if not event.transition \
       or event.transition.id not in ['submit'] \
       or obj != event.object:
        return
    ##code-section notifyCooptationPending #fill in your manual code here
    mtool = getToolByName(obj, 'portal_membership')
    prm = getToolByName(obj, 'acl_users').portal_role_manager
    # We don't manage groups on purpose, only users having directly assigned Manager role are notified
    managers = [mtool.getMemberById(manager_id) for manager_id, dontcare in prm.listAssignedPrincipals('Manager')]
    notifyCooptation(obj, "cooptation_pending_notification", recipients=managers)
    ##/code-section notifyCooptationPending


def notifyCooptationRejected(obj, event):
    """generated workflow subscriber."""
    # do only change the code section inside this function.
    if not event.transition \
       or event.transition.id not in ['reject'] \
       or obj != event.object:
        return
    ##code-section notifyCooptationRejected #fill in your manual code here
    notifyCooptation(obj, "cooptation_rejected_notification")
    ##/code-section notifyCooptationRejected


def doCooptationAcceptation(obj, event):
    """generated workflow subscriber."""
    # do only change the code section inside this function.
    if not event.transition \
       or event.transition.id not in ['accept'] \
       or obj != event.object:
        return
    ##code-section doCooptationAcceptation #fill in your manual code here
    notifyCooptation(obj, "cooptation_accepted_notification")
    ##/code-section doCooptationAcceptation


def notifyCooptationToUser(obj, actor=None, recipients=None, **kwargs):
    workspace = obj.getWorkspace()
    role = obj.getRole()
    if workspace and role:
        groupname = getattr(workspace, 'getM%sGroup' % obj.getRole())()
        gtool = getToolByName(obj, 'portal_groups')
        username = kwargs['username']
        gtool.addPrincipalToGroup(username, groupname)
    owner = obj.getOwner()
    kwargs['reviewer_name'] = owner.getProperty('fullname', None) or owner.getId()
    notifyCooptation(obj, 'cooptation_password_notification', actor=actor, recipients=recipients, **kwargs)

def notifyCooptation(obj, template_name, actor=None, recipients=None, **kwargs):
    """if not actor use AUTHENTICATED_USER
       if not recipients use obj.getOwner()
    """
    MailHost = getToolByName(obj, 'MailHost')
    if not actor:
        actor = obj.REQUEST.AUTHENTICATED_USER
    actor_fullname = actor.getProperty('fullname', None) or actor.getId()
    actor_email = actor.getProperty('email', None)
    encoding = "utf-8"
    template = getattr(obj, template_name)
    if not recipients:
        recipients = [obj.getOwner()]
    for recipient in recipients:
        if recipient is not None:
            recipient_email = recipient.getProperty('email', None)
            recipient_fullname = recipient.getProperty('fullname', None) or recipient.getId()
            if recipient_email:
                message = template(obj,
                                   obj.REQUEST,
                                   actor_fullname=actor_fullname,
                                   actor_email=actor_email,
                                   recipient_to_email=recipient_email,
                                   recipient_to_name=recipient_fullname,
                                   **kwargs)

                MailHost.send(message.encode(encoding))


##code-section module-footer #fill in your manual code here
##/code-section module-footer


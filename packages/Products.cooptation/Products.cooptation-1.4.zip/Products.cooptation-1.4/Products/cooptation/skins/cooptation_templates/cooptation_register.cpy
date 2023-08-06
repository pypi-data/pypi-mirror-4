## Controller Python Script "register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=password='password', password_confirm='password_confirm', came_from_prefs=None
##title=Register a User
##

# Copy of register.py

from Products.CMFPlone import PloneMessageFactory as PMF
from Products.cooptation.wfsubscribers import notifyCooptationToUser
from Products.CMFCore.utils import getToolByName

REQUEST = context.REQUEST

portal = context.portal_url.getPortalObject()
portal_registration = context.portal_registration

username = REQUEST['username']

password = REQUEST.get('password')

# This is a temporary work-around for an issue with CMF not properly
# reserving some existing ids (FSDV skin elements, for example). Until
# this is fixed in the CMF we can at least fail nicely. See
# http://dev.plone.org/plone/ticket/2982 and http://plone.org/collector/3028
# for more info. (rohrer 2004-10-24)
try:
    portal_registration.addMember(username, password, properties=REQUEST, REQUEST=context.REQUEST)
except AttributeError:
    state.setError('username', PMF(u'The login name you selected is already in use or is not valid. Please choose another.'))
    context.plone_utils.addPortalMessage(PMF(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')

mtool = getToolByName(context, 'portal_membership')
portal = getToolByName(context, 'portal_url').getPortalObject()
member = mtool.getMemberById(username)
notifyCooptationToUser(context,
                 recipients=[member],
                 username=username,
                 password=password,
                 portal_url=portal.absolute_url())

portal_workflow = getToolByName(context, 'portal_workflow')
if portal_workflow.getInfoFor(context, 'review_state') == 'pending':
    portal_workflow.doActionFor(context, 'accept', comment=context.REQUEST['comment'])

context.plone_utils.addPortalMessage(PMF(u'User added.'))

from Products.CMFPlone.utils import transaction_note
transaction_note('%s registered' % username)

return state

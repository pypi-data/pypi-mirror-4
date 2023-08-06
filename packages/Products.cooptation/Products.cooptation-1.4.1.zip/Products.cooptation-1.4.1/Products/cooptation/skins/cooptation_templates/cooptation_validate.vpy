## Controller Python Script "validate_registration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=username='',email='',password='',password_confirm=''
##title=validates the Registration of a User

# modified copy of join_form_validate.vpy

from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName

request = context.REQUEST
if request.form.get('edb_entite', None):
    if not isinstance(request.form['edb_entite'], (str, unicode)):
        request.form['edb_entite'] = request.form['edb_entite'][0]

reg_tool=context.portal_registration
def missing(field):
    state.setError(field, PMF(u'This field is required, please provide some information.'), 'input_required')
def nomatch(field):
    state.setError(field, PMF(u'Passwords do not match.'), 'nomatch_password')
def minlimit(field):
    state.setError(field, PMF(u'Passwords must contain at least 5 letters.'), 'min_password')
def notallowed(field):
    state.setError(field, PMF(u'This username is reserved. Please choose a different name.'), 'not_allowed')

portal = context.portal_url.getPortalObject()

if not email:
    missing('email')

wtool = getToolByName(context, 'portal_workflow')
workflow_state = wtool.getInfoFor(context, 'review_state')
if context.REQUEST.get('form.button.accept') and workflow_state == 'pending' and context.REQUEST.AUTHENTICATED_USER.has_permission('Review portal content', context):
    if not username:
        missing('username')
    if username and username == portal.getId():
        notallowed('username')

    if password!=password_confirm:
        nomatch('password')
        nomatch('password_confirm')

    if not state.getError('password') and len(password) < 5:
        minlimit('password')
        minlimit('password_confirm')

    if not state.getError('username') and not reg_tool.isMemberIdAllowed(username):
        state.setError('username',
	              PMF(u'The login name you selected is already in use or is not valid. Please choose another.'),
	              'username_invalid' )

if state.getErrors():
    context.plone_utils.addPortalMessage(PMF(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')

return state

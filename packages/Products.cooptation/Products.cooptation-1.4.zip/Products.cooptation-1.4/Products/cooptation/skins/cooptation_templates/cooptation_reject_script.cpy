## Script (Python) "cooptation_reject_script"
##title=Edit content 
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=''
##
from Products.CMFCore.utils import getToolByName

#Save changes normal way
state = context.content_edit_impl(state, id)
context = state.getContext()

portal_workflow = getToolByName(context, 'portal_workflow')
if portal_workflow.getInfoFor(context, 'review_state') == 'pending':
    portal_workflow.doActionFor(context, 'reject', comment=context.REQUEST['comment'])

state.setNextAction('redirect_to_action:string:view')
return state

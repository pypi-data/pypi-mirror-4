## Script (Python) "cooptation_accept_script"
##title=Edit content 
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=''
##

#Save changes normal way
state = context.content_edit_impl(state, id)
context = state.getContext()

context.REQUEST.set('fullname', context.Title())

state.setNextAction('traverse_to:string:cooptation_register')
return state

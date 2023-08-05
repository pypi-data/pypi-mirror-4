## Script (Python) "validate_base"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##

response = context.REQUEST.RESPONSE
response.redirect(context.absolute_url() + '/megamanic_edit_self_and_children')
## Script (Python) "megamanic_trick_macro_hack"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=object=None, fieldNameNormal=None, field=None, mode='', errors=None, request=None
##title='Another hack, quite nice?'
##

raise 'x'

allowed_to_view_edit = False

allowed = getattr(context, 'anonymousAllowedToViewEditWidget', None)
if allowed:
    if allowed():
        allowed_to_view_edit = True
    else:
        # First method we're finding that returns
        # a negative value - let's listen to that.
        allowed_to_view_edit = False

if allowed_to_view_edit:
    return context.megamanic_trick_macro(object=object, fieldNameNormal=fieldNameNormal,
                                         field=field, mode='edit', errors=errors,
                                         request=request)
else:
    return ''

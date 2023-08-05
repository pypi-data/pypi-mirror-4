## Script (Python) "validate_base"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##

from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage

from MegamanicEdit.MegamanicEdit.FakeRequest import FakeRequest

errors = {}
request = context.REQUEST
edited_objects = request.get('edited_objects', [])

if edited_objects:
    for index in range(len(edited_objects)):
        object_name = edited_objects[index]
        if index == 0 and object_name == context.getId():
            object = context
            try:
                object.setRequiredFields(request.get('required', ()))
                object.setAddSkipFields(request.get('addSkipField', ()))
                object.setTableListingFields(request.get('tableListingField', ()))
            except AttributeError:
                # Not a content generator
                pass
        else:
            object = context[object_name]
        fake_request = FakeRequest()
        for key in request.keys():
            if key.startswith(object_name):
                field_name = key[len(object_name)+1:]
                fake_request.set(field_name, request[key])
        object.processForm(REQUEST=fake_request, data=1, metadata=0)

if errors:
    message = _(u'Please correct the indicated errors.')
    addStatusMessage(request, message, type='error')
    return state.set(status='failure', errors=errors)
else:
    message = _(u'Changes saved.')
    addStatusMessage(request, message)
    return state

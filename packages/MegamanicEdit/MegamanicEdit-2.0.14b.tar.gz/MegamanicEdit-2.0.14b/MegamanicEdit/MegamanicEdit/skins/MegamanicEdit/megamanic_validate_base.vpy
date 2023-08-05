## Script (Python) "megamanic_validate_base"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##parameters=
##

from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage

from MegamanicEdit.MegamanicEdit.FakeRequest import FakeRequest

failures = {}
request = context.REQUEST
edited_objects = request.get('edited_objects', [])

if edited_objects:
    if not request.has_key('request_patched_megamanicedit'):
        request.set('request_patched_megamanicedit', [])
    for index in range(len(edited_objects)):
        object_name = edited_objects[index]
        if index == 0 and object_name == context.getId():
            object = context
        else:
            object = context[object_name]
#        fake_request = FakeRequest()
        for key in request.keys():
            if key.startswith(object_name):
                field_name = key[len(object_name)+1:]
                #fake_request.set(field_name, request[key])
                request.form.update({field_name:request[key]})
                request['request_patched_megamanicedit'].append(field_name)
        failures_ = {}
        object.validate(REQUEST=request, errors=failures_, data=1, metadata=0) # REQUEST=fake_request
        failures[object_name] = failures_
        for key in request['request_patched_megamanicedit']:
            try:
                del request.form[key]
                request['request_patched_megamanicedit'].remove(key)
            except: # Huh
                pass

if filter(None, failures.values()):
    message = _(u'Please correct the indicated failures.')
    addStatusMessage(request, message, type='error')
    return state.set(status='failure', errors=failures)
else:
    message = _(u'Changes saved.')
    addStatusMessage(request, message)
    return state

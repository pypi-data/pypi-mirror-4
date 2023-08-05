## Script (Python) "validate_base"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=adding=False
##

from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage

from MegamanicEdit.MegamanicEdit.FakeRequest import FakeRequest

errors = {}
request = context.REQUEST
edited_objects = request.get('edited_objects', [])

import random

if context.MEAddLimitReached():
   context.plone_utils.addPortalMessage('Registration limit reached', type='error')
   request.RESPONSE.redirect(context.absolute_url() + '/megamanic_add')

if edited_objects:
    created_object = None
    if 'added' not in context.objectIds():
        context.invokeFactory(id='added', type_name='Large Plone Folder')
        context['added'].title = 'Added objects'
	context.layout = 'megamanic_listing'
    added_folder = context['added']
    for index in range(len(edited_objects)):
        object_name = edited_objects[index]
        fake_request = FakeRequest()
        for key in request.keys():
            if key.startswith(object_name):
                field_name = key[len(object_name)+1:]
                fake_request.set(field_name, request[key])
        if index == 0 and object_name == context.getId():
            content_type = context.getCreateContentType()
            id = content_type.replace(' ', '-') + '-' + str(random.random())
            added_folder.invokeFactory(id=id, type_name=content_type)
            try:
                created_object = object = added_folder[id]
            except KeyError:
                raise str((id, context.objectIds()))
            # Set subject for added object
            created_object.setSubject(context.Subject())
        else:
            portal_type = context[object_name].portal_type
            id = context[object_name].getId()
            created_object.invokeFactory(id=id, type_name=portal_type)
            object = created_object[id]
        object.processForm(REQUEST=fake_request, data=1, metadata=0)
        object.setSubject(context.getSetContentSubject())

        workflow = context.portal_workflow
        for transition in context.getContentWorkflowTransitions():
            transitions = workflow.getTransitionsFor(object)
            transition_ids = [transition['id'] for transition in transitions]
            if transition in transition_ids:
                workflow.doActionFor(object, 'transition', comment='Automatic update from ME')

if errors:
    message = _(u'Please correct the indicated errors.')
    addStatusMessage(request, message, type='error')
    return state.set(status='failure', errors=errors)
else:
    request.RESPONSE.redirect('./megamanic_thanks')
    #message = _(u'Object added')
    #addStatusMessage(request, message)
return state

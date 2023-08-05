## Script (Python) "get_megamanic_editable_objects"
##title=Get objects that can be edited with MegamanicEdit
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=where,include_self=True

from Products.CMFCore.utils import getToolByName
interface = getToolByName(container, 'portal_interface')

#MegamanicEditable = 'MegamanicEdit.MegamanicEdit.MegamanicEdit.interfaces.MegamanicEditableObject'

editable = []

if include_self:
    editable.append(where)

for object in where.contentValues():
    # For some reason this doesn't work, so we hack it
    #if interface.objectImplements(object, MegamanicEditable):
    MegamanicEditable = getattr(object, 'isMegamanicEditable', '')
    if MegamanicEditable and MegamanicEditable(object):
        editable.append(object)

return editable

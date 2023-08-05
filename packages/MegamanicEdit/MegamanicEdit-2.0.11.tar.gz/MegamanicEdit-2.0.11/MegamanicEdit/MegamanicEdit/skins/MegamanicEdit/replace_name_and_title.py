## Script (Python) "replace_name_and_title"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##parameters=old,fieldNameNormal,fieldName
##

old = old.replace('name="' + fieldNameNormal + '"',
                   'name="' + fieldName + '"' + """ onfocus="clear_if_default('%s');" """ % fieldName)
# For textareas/rich fields
old = old.replace('name="' + fieldNameNormal + '_text_format"',
                   'name="' + fieldName + '_text_format"')

# Heh
new = old

return new

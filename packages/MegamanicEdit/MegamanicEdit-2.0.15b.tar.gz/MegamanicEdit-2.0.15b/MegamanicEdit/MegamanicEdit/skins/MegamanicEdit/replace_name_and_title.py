## Script (Python) "replace_name_and_title"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##parameters=old,fieldNameNormal,fieldName
##

old = old.replace('name="' + fieldNameNormal + '"',
                   'name="' + fieldName + '"' + """ onfocus="clear_if_default('%s');" """ % fieldName)
# For textareas/rich fields and :lines
old = old.replace('name="' + fieldNameNormal + '_text_format"',
                   'name="' + fieldName + '_text_format"')

old = old.replace('name="' + fieldNameNormal + '_keywords:lines"',
                   'name="' + fieldName + '_keywords:lines"')

# Heh
new = old

return new

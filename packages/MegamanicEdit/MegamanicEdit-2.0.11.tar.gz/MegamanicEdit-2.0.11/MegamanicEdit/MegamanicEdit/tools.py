from Products.Archetypes.Widget import PasswordWidget
from interfaces import MegamanicEditableTemplateObject

def setup(klass):
    schema = klass.schema
    enable_postback(schema)
    if MegamanicEditableTemplateObject.implementedBy(klass) and schema.has_key('subject'):
        schema.changeSchemataForField('subject', 'default')

def enable_postback(schema):
    """Enables postback for all schema fields, except password."""
    for field in schema.fields():
        if not field.widget.__class__ is PasswordWidget:
            field.widget._properties['postback'] = True

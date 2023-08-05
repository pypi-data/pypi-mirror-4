from zope.interface import Interface

class MegamanicEditableObject(Interface):
    """Indicates whether this object has objects or
    fields for MegamanicEdit."""

    def isMegamanicEditable():
        "Exists and returns true if the object is MegamanicEditable"

    def getMegamanicEditableFields():
        "Returns an ordered list of editable fields (as strings)."

    def megamanicHackRequest():
        "Alters the request to edit multiple objects and fields."

    def megamanicHackRequestClear():
        "Clears the request after multiple editing of objects."

    def isMegamanicEditableTemplateObject(self):   
        """Returns true if object is a template object."""

class MegamanicEditableTemplateObject(MegamanicEditableObject):
    """Indicates whether this object has support
    for the MegamanicEditableTemplateObject class."""
    pass

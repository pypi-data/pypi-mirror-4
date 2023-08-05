from Products.Archetypes.Field import Field

checkPermissionOld = Field.checkPermission

def checkPermission(self, mode, instance):
    """Hacks access to add widgets.."""
    aatvew = getattr(instance, 'anonymousAllowedToViewEditWidget', None)
    if aatvew and callable(aatvew) and aatvew.im_func(instance):
        return True
    else:
        return checkPermissionOld(self, mode, instance)

Field.checkPermission = checkPermission

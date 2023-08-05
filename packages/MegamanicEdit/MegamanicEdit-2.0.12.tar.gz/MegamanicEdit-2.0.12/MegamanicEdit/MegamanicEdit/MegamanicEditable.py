from zope.interface import implements
from interfaces import MegamanicEditableObject, MegamanicEditableTemplateObject
from Products.CMFCore.permissions import ModifyPortalContent

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.Archetypes import atapi

templateObjectSchema = atapi.Schema((

    atapi.StringField(
        name='createContentType',
        required=0,
        searchable=0,
        default='',
        vocabulary='getMegamanicAllowedTypes',
        widget=atapi.SelectionWidget()
    ),

    atapi.TextField('submitBody',
        required = False,
        searchable = True,
        primary = False,
        validators = ('isTidyHtmlWithCleanup',),
        default='Enter information here to register',
        #validators = ('isTidyHtml',),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(
            description = '',
            rows = 25,
        ),
    ),

    atapi.StringField(
        name='thanksTitle',
        required=0,
        searchable=0,
        default='Thank you!',
    ),

    atapi.TextField('thanksBody',
        required = False,
        searchable = True,
        primary = False,
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default='Thank you for registering',
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(
            description = '',
            rows = 25,
        ),
    ),

    atapi.LinesField(
        name='setContentSubject',
        required=0,
        searchable=0,
        default=(),
    ),


    atapi.BooleanField(
        name='allowAnonymousAdd',
        required=0,
        searchable=0,
        mutator='setAllowAnonymousAdd',
#        mode='r',
        default=True,
    ),

# Re-enable when member adding is mature
#    atapi.BooleanField(
#        name='allowMemberAdd',
#        required=0,
#        searchable=0,
#        mutator='setAllowMemberAdd',
##        mode='r',
#        default=False,
#    ),

    atapi.LinesField(
        name='tableListingFields',
        required=0,
        searchable=0,
        default=('title', 'description'),
        schemata='hacks'
    ),

    atapi.LinesField(
        name='requiredFields',
        required=0,
        searchable=0,
        default='',
        schemata='hacks'
    ),

    atapi.LinesField(
        name='addSkipFields',
        required=0,
        searchable=0,
        default='',
        schemata='hacks',
    ),

    atapi.LinesField(
        name='contentWorkflowTransitions',
        required=0,
        searchable=0,
        default=('retract', 'hide'),
        schemata='hacks',
    ),

))


class MegamanicEditable:
    implements(MegamanicEditableObject)

    security = ClassSecurityInfo()

    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        parent = self.getParentNode()
        #if self.isMegamanicEditableTemplateObject() and \
        #        self.getAllowAnonymousAdd():
        #    self.plone_utils.addPortalMessage('Remember to publish this object (make viewable) %s as well' % self.getId())
        # A class inheriting from MegamanicEdit must always have a MegamanicEdit
        # class as the first superclass
        for base in self.__class__.__bases__[1:]:
            if hasattr(base, 'at_post_create_script'):
                base.at_post_create_script(self)
                break

    security.declarePublic('isMegamanicEditable')
    def isMegamanicEditable(self, object=None):
        "Yes it is."
        if object is None: object = self
        # Why portal_interfaces doesn't see the implementation is beyond me.
        return MegamanicEditableObject.implementedBy(object.__class__)

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('title', 'description')

    security.declarePublic('megamanicHackRequest')
    def megamanicHackRequest(self, object):
        """Hacks the request so we can edit things."""
        object_name = object.getId()
        request = self.REQUEST
        request.set('megamanic_edit_hack_request', [])

        for key in request.form.keys():
            if key.startswith(object_name):
                field_name = key[len(object_name)+1:]
                request.form[field_name] = request[key]
                request['megamanic_edit_hack_request'].append(field_name)

    security.declarePublic('megamanicHackRequestClear')
    def megamanicHackRequestClear(self):
        """Clears the request after modifying it to edit things."""
        request = self.REQUEST
        for name in request.get('megamanic_edit_hack_request', []):
            del request.form[name]

    security.declarePublic('isMegamanicEditableTemplateObject')
    def isMegamanicEditableTemplateObject(self, object=None):
        """Returns true if we're a template object."""
        return False

    def getMegamanicAllowedTypes(self):
        """Returns a list of allowed types."""
        types = []
        for content_type in self.getAllowedTypes():
            types.append(content_type.content_meta_type)
        return types

    def getTitle(self):
        """Returns the title."""
        return self.Title()

from zExceptions import BadRequest

class MegamanicEditableTemplateObject(MegamanicEditable):

    security = ClassSecurityInfo()
    implements(MegamanicEditableTemplateObject)

    security.declarePublic('getMEAddLimitReached')
    def MEAddLimitReached(self):
        """Returns the max number of megamanic_add added objects."""
        try:
            return self.getParentNode().MEAddLimitReached()
        except AttributeError:
            return False

    def manage_afterAdd(self, item, container):
        """Adds necessary things.."""
        # Why AT default doesn't kick in beats me
        try:
            try:
                self.invokeFactory(id='added', type_name='Large Plone Folder', title='Add Objects')
            except ValueError:
                # Plone 4, no large plone folder
                self.invokeFactory(id='added', type_name='Folder', title='Add Objects')
            self.setAllowAnonymousAdd(allow=True)
            self.manage_permission('Modify view template', roles=[], acquire=0)
            self.added.setLayout('megamanic_listing')
        except BadRequest:
            # Called after rename operation probably
            pass

    security.declarePublic('getMegamanicEditableTemplateObject')
    def isMegamanicEditableTemplateObject(self, object=None):
        """Returns true if we're a template object."""
        return True

    def setAllowAnonymousAdd(self, allow=False):
        """Set allow anonymous add if necessary."""
        self.schema['allowAnonymousAdd'].set(self, allow)
        if not hasattr(self.aq_base, 'added'):
            # Before manage_afterAdd
            return None
        if allow:
            self.added.manage_permission('Add portal content', roles=['Anonymous'])
            self.added.manage_permission('View', roles=['Editor', 'Manager', 'Owner',], acquire=0)
            self.added.manage_permission('Access contents information', roles=['Anonymous'])
            for content in self.contentValues():
                if content.id != 'added':
                    content.manage_permission('View', roles=['Anonymous'])
                    content.manage_permission('Access contents information', roles=['Anonymous'])
            self.plone_utils.addPortalMessage('Remember to publish (make viewable for non-logged-in users) this object (%s) as well' % self.getId())
        else:
            self.added.manage_permission('Add portal content', roles=[], acquire=1)
            self.added.manage_permission('View', roles=[], acquire=1)
            self.added.manage_permission('Access contents information', roles=[], acquire=1)
            for content in self.contentValues():
                if content.id != 'added':
                    content.manage_permission('View', roles=[], acquire=1)
                    content.manage_permission('Access contents information', roles=[], acquire=1)

    def setAllowMemberAdd(self, allow=False):
        """Set allow member add if necessary."""
        self.schema['allowMemberAdd'].set(self, allow)
        if not hasattr(self.aq_base, 'added'):
            # Before manage_afterAdd
            return None
        # Assuming that property gets set before this one
        if self.getAllowAnonymousAdd(): return
        if allow:
            self.added.manage_permission('Add portal content', roles=['Member', 'Manager'])
            self.added.manage_permission('View', roles=['Editor', 'Manager', 'Owner',], acquire=0)
            self.added.manage_permission('Access contents information', roles=['Member', 'Manager'])
            for content in self.contentValues():
                if content.id != 'added':
                    content.manage_permission('View', roles=['Member', 'Manager'])
                    content.manage_permission('Access contents information', roles=['Member', 'Manager'])
        else:
            self.added.manage_permission('Add portal content', roles=[], acquire=1)
            self.added.manage_permission('View', roles=[], acquire=1)
            self.added.manage_permission('Access contents information', roles=[], acquire=1)
            for content in self.contentValues():
                if content.id != 'added':
                    content.manage_permission('View', roles=[], acquire=1)
                    content.manage_permission('Access contents information', roles=[], acquire=1)

    def anonymousAllowedToViewEditWidget(self):
        """Returns a truth value if Anonymous can view edit widgets."""
        return False

    def getMegamanicTableListingFields(self):
        """Returns fields used in the table listing."""
        fields = self.getTableListingFields()
        fields_ = []
        for field in fields:
            if not field in fields_:
                title = '_'.join(field.split('-')[-1].split('_')[1:])
                object_name = field[:field.find('_')]
                if object_name == self.getId():
                    object = None
                else:
                    object = object_name
                fields_.append((title, object))
        return fields_

    def getCSV(self):
        """Returns a CSV file of added objects."""
        import csv
        from cStringIO import StringIO
        file = StringIO()
        # Most people use Excel, so let's assume it's OK
        csv.writer(file, dialect='excel')
        for object in self.added.objectValues():
            fields = []
            for field in object.getMegamanicEditableFields():
                fields.append(getattr, object + 'get' + field.capitalize())
        pass # XXX

InitializeClass(MegamanicEditable)
InitializeClass(MegamanicEditableTemplateObject)

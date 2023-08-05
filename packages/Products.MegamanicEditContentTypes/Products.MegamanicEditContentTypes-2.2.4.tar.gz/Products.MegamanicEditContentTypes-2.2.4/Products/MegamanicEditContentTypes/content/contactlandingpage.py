"""Definition of the Contact content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.CMFCore.permissions import ManagePortal, View

# -*- Message Factory Imported Here -*-

from Products.MegamanicEditContentTypes.interfaces import IContactlandingpage
from Products.MegamanicEditContentTypes.config import PROJECTNAME

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

ContactSchema = folder.ATFolderSchema.copy() + MegamanicEditable.templateObjectSchema.copy()
# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ContactSchema['title'].storage = atapi.AnnotationStorage()
ContactSchema['title'].widget = atapi.StringWidget(label='Fullname',
                                                   size=30)
ContactSchema['description'].storage = atapi.AnnotationStorage()
ContactSchema['description'].storage = atapi.AnnotationStorage()
ContactSchema['createContentType'].default = 'Contact'
ContactSchema['setContentSubject'].default = ('Landing page',)

schemata.finalizeATCTSchema(
    ContactSchema,
    folderish=True,
    moveDiscussion=False
)

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Contactlandingpage(MegamanicEditable.MegamanicEditableTemplateObject, folder.ATFolder, ):
    """Description of the Contact landing page type"""

    implements(IContactlandingpage)

    meta_type = "Contactlandingpage"
    schema = ContactSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declareProtected(View, 'getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('title', 'description', 'createContentType')

    security.declareProtected(View, 'anonymousAllowedToViewEditWidget')
    def anonymousAllowedToViewEditWidget(self):
        """Returns true if anonymous can add."""
        return self.getAllowAnonymousAdd()

InitializeClass(Contactlandingpage)
atapi.registerType(Contactlandingpage, PROJECTNAME)
tools.setup(Contactlandingpage)

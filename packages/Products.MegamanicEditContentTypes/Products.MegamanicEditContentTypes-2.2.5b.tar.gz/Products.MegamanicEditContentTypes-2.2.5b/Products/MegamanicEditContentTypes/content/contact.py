"""Definition of the Contact content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from Products.MegamanicEditContentTypes.interfaces import IContact
from Products.MegamanicEditContentTypes.config import PROJECTNAME

from Products.CMFCore.permissions import ManagePortal, View

ContactSchema = folder.ATFolderSchema.copy() + atapi.Schema((

)) 

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ContactSchema['title'].storage = atapi.AnnotationStorage()
#ContactSchema['title'].label = 'Fullname'
ContactSchema['title'].widget = atapi.StringWidget(label = 'Fullname')
ContactSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ContactSchema,
    folderish=True,
    moveDiscussion=False
)

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Contact(MegamanicEditable.MegamanicEditable, folder.ATFolder,):
    """Description of the Example Type"""
    implements(IContact)

    meta_type = "Contact"
    schema = ContactSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def manage_afterAdd(self, a, b):
        """Hook to add some default things."""

    security.declareProtected(View, 'getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('title', 'description')

    security.declareProtected(View, 'getMegamanicEditableFields')
    def getEmailAddresses(self):
        """Returns the email adresses contained."""
        return filter(None, map(lambda x: x.getEmail(), self.objectValues('Emailaddress')))

InitializeClass(Contact)
atapi.registerType(Contact, PROJECTNAME)
tools.setup(Contact)

"""Definition of the Email address content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.MegamanicEditContentTypes.interfaces import IEmailaddress
from Products.MegamanicEditContentTypes.config import PROJECTNAME

from VariousDisplayWidgets.VariousDisplayWidgets.widgets.Email import EmailWidget

EmailaddressSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.StringField(
        name='email',
        required=1,
        searchable=1,
        default='',
        validators=('isEmail',),
        size=40,
        widget=EmailWidget()
    )

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

EmailaddressSchema['title'].storage = atapi.AnnotationStorage()
EmailaddressSchema['title'].widget.visible = {'edit' : 'invisible', 'view':'visible'}
EmailaddressSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    EmailaddressSchema,
    folderish=True,
    moveDiscussion=False
)

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Emailaddress(MegamanicEditable.MegamanicEditable, folder.ATFolder,):
    """ """
    implements(IEmailaddress)

    meta_type = "Emailaddress"
    schema = EmailaddressSchema

    security = ClassSecurityInfo()
    
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('email', 'description')

    security.declarePublic('validateMainField')
    def validateMainField(self, email=''):
        """Validates that the value given is acceptable."""
        return not self.schema['email'].validate(email, self)

    def Title(self):
        """Returns a proper title."""
        return 'Email address'

InitializeClass(Emailaddress)
atapi.registerType(Emailaddress, PROJECTNAME)
tools.setup(Emailaddress)

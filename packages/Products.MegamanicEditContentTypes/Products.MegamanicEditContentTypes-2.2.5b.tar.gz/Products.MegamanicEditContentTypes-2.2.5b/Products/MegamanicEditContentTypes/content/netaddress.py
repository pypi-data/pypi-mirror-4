"""Definition of the Contact net address content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.MegamanicEditContentTypes.interfaces import INetaddress
from Products.MegamanicEditContentTypes.config import PROJECTNAME

from VariousDisplayWidgets.VariousDisplayWidgets.widgets.URI import URIWidget

NetaddressSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        name='address',
        required=1,
        searchable=1,
        default='',
        validators=('isURL',),
        size=40,
        widget=URIWidget(),
    )

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

NetaddressSchema['title'].storage = atapi.AnnotationStorage()
NetaddressSchema['title'].widget.visible = {'edit' : 'invisible', 'view':'visible'}
NetaddressSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    NetaddressSchema,
    folderish=True,
    moveDiscussion=False
)

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Netaddress(MegamanicEditable.MegamanicEditable, folder.ATFolder,):
    """Description of the Example Type"""
    implements(INetaddress)

    meta_type = "Netaddress"
    schema = NetaddressSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('address', 'description')

    security.declarePublic('validateMainField')
    def validateMainField(self, address=''):
        """Validates that the value given is acceptable."""
        return not self.schema['address'].validate(address, self)

    def Title(self):
        """Returns a proper title."""
        return 'Net (web) address'

# Redundant to hvae InitializeClass?
InitializeClass(Netaddress)
atapi.registerType(Netaddress, PROJECTNAME)
tools.setup(Netaddress)

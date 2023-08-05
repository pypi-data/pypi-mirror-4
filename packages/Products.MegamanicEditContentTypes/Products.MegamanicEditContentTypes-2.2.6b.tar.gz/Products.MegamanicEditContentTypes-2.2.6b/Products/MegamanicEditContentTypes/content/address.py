"""Definition of the Contact address content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.MegamanicEditContentTypes.interfaces import IAddress
from Products.MegamanicEditContentTypes.config import PROJECTNAME

from VariousDisplayWidgets.VariousDisplayWidgets.widgets.URI import URIWidget

AddressSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField(
        name='name_or_co',
        required=0,
        searchable=1,
        default='',
        size=40,
        widget=atapi.StringWidget(label='Name or CO (recipient)')
    ),
    atapi.StringField(
        name='street',
        required=0,
        searchable=1,
        default='',
        size=40,
        widget=atapi.StringWidget(label='Street')
    ),
    atapi.StringField(
        name='postal_code',
        required=0,
        searchable=1,
        default='',
        size=40,
        widget=atapi.StringWidget(label='Postal code')
    ),
    atapi.StringField(
        name='postal_area',
        required=0,
        searchable=1,
        default='',
        size=40,
        widget=atapi.StringWidget(label='Postal area')
    ),
    atapi.StringField(
        name='region',
        required=0,
        searchable=1,
        default='',
        size=40,
        widget=atapi.StringWidget(label='Region')
    ),
    atapi.StringField(
        name='state',
        required=0,
        searchable=1,
        default='',
        size=40,
        widget=atapi.StringWidget(label='State')
    )

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AddressSchema['title'].storage = atapi.AnnotationStorage()
AddressSchema['title'].widget.visible = {'edit' : 'invisible', 'view':'visible'}
AddressSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    AddressSchema,
    folderish=True,
    moveDiscussion=False
)

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Address(MegamanicEditable.MegamanicEditable, folder.ATFolder):
    """Description of the Example Type"""
    implements(IAddress)

    meta_type = "Address"
    schema = AddressSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('name_or_co', 'street', 'postal_code', 'postal_area',
                'region', 'state', 'description',)

    security.declarePublic('validateMainField')
    def validateMainField(self, address=''):
        """Validates that the value given is acceptable."""
        return not self.schema['address'].validate(address, self)

    def Title(self):
        """Returns a proper title."""
        return 'Physical address'

# Redundant to hvae InitializeClass?
InitializeClass(Address)
atapi.registerType(Address, PROJECTNAME)
tools.setup(Address)

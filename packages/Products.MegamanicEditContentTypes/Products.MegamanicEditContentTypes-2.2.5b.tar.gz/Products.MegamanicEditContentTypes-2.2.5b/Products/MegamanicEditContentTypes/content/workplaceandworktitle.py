"""Definition of the Contact workplace and work title content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.MegamanicEditContentTypes.interfaces import IWorkplaceandworktitle
from Products.MegamanicEditContentTypes.config import PROJECTNAME

WorkplaceandworktitleSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.StringField(
        name='employer',
        label='Employer',
        required=1,
        searchable=1,
        default='',
        validators=(),
        size=40,
    ),

    atapi.StringField(
        name='job_title',
        label='Job title',
        required=1,
        searchable=1,
        default='',
        validators=(),
        size=40,
    )

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

WorkplaceandworktitleSchema['title'].storage = atapi.AnnotationStorage()
WorkplaceandworktitleSchema['title'].widget.visible = {'edit' : 'invisible', 'view':'visible'}
# Looks like contact.py is bleeding into this schema
WorkplaceandworktitleSchema['employer'].widget.label = 'Employer'
WorkplaceandworktitleSchema['job_title'].widget.label = 'Job title'
WorkplaceandworktitleSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    WorkplaceandworktitleSchema,
    folderish=True,
    moveDiscussion=False
)

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Workplaceandworktitle(MegamanicEditable.MegamanicEditable, folder.ATFolder,):
    """Description of the Example Type"""
    implements(IWorkplaceandworktitle)

    meta_type = "Workplaceandworktitle"
    schema = WorkplaceandworktitleSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('employer', 'job_title', 'description')

    security.declarePublic('validateMainField')
    def validateMainField(self, employer='', job_title=''):
        """Validates that the value given is acceptable."""
        return (not self.schema['employer'].validate(employer, self)) and \
                (not self.schema['job_title'].validate(job_title, self))

    def Title(self):
        """Returns a proper title."""
        return 'Workplace and title'

InitializeClass(Workplaceandworktitle)
atapi.registerType(Workplaceandworktitle, PROJECTNAME)
tools.setup(Workplaceandworktitle)

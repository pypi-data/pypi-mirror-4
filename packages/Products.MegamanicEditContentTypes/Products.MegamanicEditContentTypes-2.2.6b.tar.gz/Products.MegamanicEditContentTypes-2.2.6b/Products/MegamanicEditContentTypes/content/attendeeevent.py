"""Definition of the Contact net address content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import event
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.MegamanicEditContentTypes.interfaces import IAttendeeEvent
from Products.MegamanicEditContentTypes.config import PROJECTNAME

from VariousDisplayWidgets.VariousDisplayWidgets.widgets.URI import URIWidget

AttendeeEventSchema = folder.ATFolderSchema.copy() + event.ATEventSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.IntegerField(
        name='attendeeLimit',
        required=1,
        default=0, # No limit
        size=40,
        widget=atapi.IntegerWidget(label='Attendee limit, 0 means no limit')
    ),

    atapi.ComputedField(
            name='registered',
            expression='len(context.getMEAddedContacts())',)

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AttendeeEventSchema['title'].storage = atapi.AnnotationStorage()
AttendeeEventSchema['description'].storage = atapi.AnnotationStorage()
# Because calendar_macros is too funky
AttendeeEventSchema['startDate'].widget = atapi.StringWidget(label='Start date')
AttendeeEventSchema['endDate'].widget = atapi.StringWidget(label='End date')
AttendeeEventSchema['attendees'].widget.visible = {'edit' : 'invisible', 'view':'invisible'}
AttendeeEventSchema['eventUrl'].widget = URIWidget(label='Event URL')
AttendeeEventSchema['text'].default = u'Go <a href="./registrations/megamanic_add">here to register</a>'

schemata.finalizeATCTSchema(
    AttendeeEventSchema,
    folderish=True,
    moveDiscussion=False
)

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# To avoid security checks
from Products.ZCatalog.ZCatalog import ZCatalog

class AttendeeEvent(folder.ATFolder, event.ATEvent, MegamanicEditable.MegamanicEditable):
    """Description of the Attendee event Type"""
    implements(IAttendeeEvent)

    meta_type = "Attendee event"
    schema = AttendeeEventSchema

    security = ClassSecurityInfo()

    def manage_afterAdd(self, *a, **kw):
        try:
            self.invokeFactory(id='registrations', type_name='Contact landing page')
            self['registrations'].setTitle('Registration')
            self['registrations'].setTableListingFields(('title', 'description'))
        except: pass
        

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('title', 'description', 'attendeeLimit', 'location',
                'startDate', 'endDate', 'text', 'subject', 'eventUrl',
                'contactName', 'contactEmail', 'contactPhone')

    def getMEAddedContacts(self):
        """Returns a list of attendees (implementing the IContact interface)."""
        results = ZCatalog.searchResults.im_func(self.portal_catalog,
            object_provides='Products.MegamanicEditContentTypes.interfaces.IContact',
            path='/'.join(self.getPhysicalPath()))
        return results

    security.declarePublic('getMEAddLimitReached')
    def MEAddLimitReached(self):
        """Returns true if megamanic_add added objects limit is reached."""
        attendees = self.getMEAddedContacts()
        limit = self.getAttendeeLimit()
        return limit and len(attendees) >= limit

# Redundant to hvae InitializeClass?
InitializeClass(AttendeeEvent)
atapi.registerType(AttendeeEvent, PROJECTNAME)
tools.setup(AttendeeEvent)

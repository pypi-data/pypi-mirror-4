from zope.interface import Interface

class IEmailaddress(Interface):
    """Description of the Email address type"""
    pass

class INetaddress(Interface):
    """Description of the Net address Type"""

class IAddress(Interface):
    """Description of the Address Type"""

class IPhonenumber(Interface):
    """Description of the Phone number Type"""

class IWorkplaceandworktitle(Interface):
    """Description of the Work place and work title Type"""

class IContact(Interface):
    """Description of the Contact Type"""

#    def getEmailAddresses():
#        "Returns a list of email addresses."""

class IContactlandingpage(Interface):
    """Description of the Contact landing page Type"""

class IEmailMessage(Interface):
    """Description of the EmailMessage Type interface"""
    pass

class IAttendeeEvent(Interface):
    """Description of the AttendeeEvent interface"""
    pass

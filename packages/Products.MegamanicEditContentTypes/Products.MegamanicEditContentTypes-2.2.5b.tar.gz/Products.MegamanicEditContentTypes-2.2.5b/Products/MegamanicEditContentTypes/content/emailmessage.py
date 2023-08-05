"""Definition of the Email message content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from Products.MegamanicEditContentTypes.interfaces import IEmailMessage
from Products.MegamanicEditContentTypes.config import PROJECTNAME

EmailMessageSchema = folder.ATFolderSchema.copy() + atapi.Schema((
        atapi.StringField('sender', label='Sender', required=True,
                          storage=atapi.AnnotationStorage(),
                          validators=('rfc822AddressField',),
                          widget=atapi.StringWidget(label='Sender', size=50)
                          ),
        atapi.TextField('to', label='To', required=True,
                        storage=atapi.AnnotationStorage(),
                        validators=('rfc822AddressField',),
                        widget=atapi.TextAreaWidget(rows=3, cols=30, label='To'),),
        atapi.TextField('cc', label='Carbon copies (CC)',
                        storage=atapi.AnnotationStorage(),
                        validators=('rfc822AddressField',),
                        widget=atapi.TextAreaWidget(rows=3, cols=30, label='Carbon copies (CC)'),),
        atapi.TextField('bcc', label='Invisible copies (BCC)',
                        storage=atapi.AnnotationStorage(),
                        validators=('rfc822AddressField',),
                        widget=atapi.TextAreaWidget(rows=3, cols=30, label='Invisible copies (BCC)'), ),
        atapi.TextField('body', required=True,
                        storage=atapi.AnnotationStorage(),
                        widget=atapi.RichWidget(rows=25)),
))

EmailMessageSchema['title'].storage = atapi.AnnotationStorage()
EmailMessageSchema['title'].label = 'Subject'
EmailMessageSchema['title'].widget.label = 'Subject'
EmailMessageSchema['description'].storage = atapi.AnnotationStorage()
EmailMessageSchema['description'].widget.visible = {'edit':'invisible', 'view':'invisible'}

schemata.finalizeATCTSchema(
    EmailMessageSchema,
    folderish=True,
    moveDiscussion=False
)

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

EMAIL_4 = False
global EMAIL_4
try:
    import email
    from email import message
    if hasattr(email, 'backport'):
        email.backport()
    EMAIL_4 = True
except ImportError:
    import email_backport as email
    email.backport()
    EMAIL_4 = True

if EMAIL_4:
    from email import utils
    from email.header import Header
        
message_template = """Subject: %s
Sender: %s
To: %s
Cc: %s
Content-Type: text/html; charset=utf-8

%s
"""

message_template_archive = """Subject: %s
Sender: %s
To: %s
Cc: %s
Bcc: %s
Content-Type: text/html; charset=utf-8

%s
"""

class EmailMessage(MegamanicEditable.MegamanicEditable, folder.ATFolder,):
    """The Email message content type."""
    implements(IEmailMessage)

    meta_type = "Email message"
    schema = EmailMessageSchema

    security = ClassSecurityInfo()

    def initializeArchetype(self, **kw):
        folder.ATFolder.initializeArchetype.im_func(*(self,), **kw)
        self.setup_for_edit()
        self.manage_permission('View', ['Owner', 'Manager'], acquire=0)
        #workflow = self.portal_workflow
        #transitions = workflow.getTransitionsFor(self)
        #transition_ids = [transition['id'] for transition in transitions]
        #if 'retract' in transition_ids:
        #    workflow.doActionFor(self, 'retract', comment='Automatic hiding')
        #transitions = workflow.getTransitionsFor(self)
        #transition_ids = [transition['id'] for transition in transitions]
        #if 'hide' in transition_ids:
        #    workflow.doActionFor(self, 'hide', comment='Automatic hiding')

    def setup_for_edit(self, *a, **kw):
        "Sets up an email message if created from somewhere"
        session = self.REQUEST.SESSION
        if not session.get('setup_email', False): return
        del session['setup_email']
        for key in ('sender', 'to', 'cc', 'bcc', 'title', 'body'):
            try:
                getattr(self, 'set' + key.capitalize())(session[key])
                del session[key]
            except Exception, value:
                print 'Exception', value
        if not self.getSender().strip():
            member = self.portal_membership.getAuthenticatedMember()
            self.setSender('"%s" <%s>' % (member.getProperty('fullname'), member.getProperty('email')))

    def mail_enabled(self):
        "Returns true if mail is enabled."
        return EMAIL_4

    def send_email_message(self):
        "Sends a message."
        subject = Header(self.Title(), 'utf-8')
        sender = self.getSender()
        to = self.getTo()
        cc = self.getCc()
        bcc = self.getBcc()
        body = self.getBody(raw=True)
        sent = message_template % (subject, sender, to, cc, body)
        archive = message_template_archive % (subject, sender, to, cc, bcc, body)
        self.MailHost.send(sent, self.get_recipient_emails(), sender)
        self.plone_utils.addPortalMessage('Message sent', type='info')
        self.REQUEST.RESPONSE.redirect(self.absolute_url())

    def get_recipient_emails(self):
        """Returns a list of recipient emails, To, CC and BCC."""
        to = self.getTo()
        cc = self.getCc()
        bcc = self.getBcc()
        emails = []
        for field in to, cc, bcc:
            emails.extend(map(lambda x: utils.parseaddr(x)[1], field.split(',')))
        return emails

InitializeClass(EmailMessage)
atapi.registerType(EmailMessage, PROJECTNAME)
tools.setup(EmailMessage)

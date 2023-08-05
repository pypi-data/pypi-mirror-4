## Script (Python) "create_email"
##bind container=container                                                                                                          
##bind context=context                                                                                                              
##bind namespace=                                                                                                                   
##bind script=script                                                                                                                
##parameters=sender='',to='',cc='',bcc='',subject='',body=''
##                                                                        

request = context.REQUEST
session = request.SESSION
session['setup_email'] = True
session['sender'] = sender
session['to'] = ''
to_ = ''
if hasattr(to, 'append'):
    for entry in to:
        if not entry.strip(): continue
        if to_:
            to_ += ','
        to_ += entry
    session['to'] = to_
else:
    session['to'] = to
session['cc'] = cc
session['bcc'] = bcc
session['title'] = subject
session['body'] = body

membership = context.portal_membership
home_folder = membership.getHomeFolder()
if home_folder is None:
    membership.createMemberArea()
    home_folder = membership.getHomeFolder()
    if home_folder is None:
        context.plone_utils.addPortalMessage('Enable user folders in the site setup security panel', type='error')
        request.RESPONSE.redirect(request['HTTP_REFERER'])
        return
if not hasattr(home_folder, 'emails'):
     home_folder.invokeFactory(id='emails', type_name='Folder')

request.RESPONSE.redirect(home_folder.emails.absolute_url() + '/createObject?type_name=Email+message')

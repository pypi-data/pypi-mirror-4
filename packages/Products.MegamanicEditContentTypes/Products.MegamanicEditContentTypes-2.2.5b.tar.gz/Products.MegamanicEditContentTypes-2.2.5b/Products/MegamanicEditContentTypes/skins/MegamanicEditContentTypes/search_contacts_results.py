## Script (Python) "create_email"
##bind container=container                                                                                                          
##bind context=context                                                                                                              
##bind namespace=                                                                                                                   
##bind script=script                                                                                                                
##parameters=
##                                                                        

request = context.REQUEST
query = {'object_provides':'Products.MegamanicEditContentTypes.interfaces.IContact'}
if request.has_key('SearchableText'):
    # We have a submission
    if request.SearchableText.strip():
        query['SearchableText'] = request['SearchableText']
    if not request.has_key('search_all_subjects'):
        if request.get('Subject', []):
            query['Subject'] = request['Subject']

return map(lambda x: x.getObject(), context.portal_catalog(**query))

from zope.i18nmessageid import MessageFactory
from Products.MegamanicEditContentTypes import config

from Products.Archetypes import atapi
from Products.CMFCore import utils

MegamanicEditContentTypesMessageFactory = MessageFactory('Products.MegamanicEditContentTypes')

from Products.ATContentTypes.config import HAS_LINGUA_PLONE

if not HAS_LINGUA_PLONE:
    from Products.Archetypes.atapi import process_types, listTypes
else:
    from Products.LinguaPlone.public import process_types, listTypes

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    listOfTypes = listTypes(config.PROJECTNAME)

    content_types, constructors, ftis = process_types(listOfTypes, config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types=(atype,),
            permission='Add portal content',
            extra_constructors=(constructor,),
            ).initialize(context)


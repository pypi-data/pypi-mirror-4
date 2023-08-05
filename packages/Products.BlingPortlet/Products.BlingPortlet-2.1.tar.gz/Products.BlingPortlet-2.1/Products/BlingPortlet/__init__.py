from Products.Archetypes import atapi
from Products.CMFCore import utils
from zope.i18nmessageid import MessageFactory


BlingPortletMessageFactory = MessageFactory('Products.BlingPortlet')

import content

ADD_PERMISSIONS = {
    'LinkableImage': 'BlingPortlet: Add Linkable Image'
}

PRODUCT_NAME = 'BlingPortlet'

def initialize(context):
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(PRODUCT_NAME),
        PRODUCT_NAME)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (PRODUCT_NAME, atype.portal_type),
            content_types      = (atype,),
            permission         = ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)
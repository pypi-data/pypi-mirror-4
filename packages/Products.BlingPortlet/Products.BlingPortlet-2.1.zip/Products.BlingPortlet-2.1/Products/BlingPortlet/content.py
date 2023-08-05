from Products.ATContentTypes.content.image import ATImageSchema, ATImage
from Products.Archetypes import atapi
from Products.BlingPortlet import BlingPortletMessageFactory as _
from Products.BlingPortlet.interfaces import ILinkableImage
from Products.Five.browser import BrowserView
from zope.interface import implements


LinkableImageSchema = ATImageSchema.copy() + atapi.Schema((

    atapi.TextField('link',
        widget = atapi.StringWidget(
            label = _(u'Link'),
            description = _(u'A link for the image.'),
        ),
    ),

))

class LinkableImage(ATImage):
    """A Linkable Image"""
    implements(ILinkableImage)

    meta_type = "LinkableImage"
    schema = LinkableImageSchema

atapi.registerType(LinkableImage, "BlingPortlet")

class LinkableImageView(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

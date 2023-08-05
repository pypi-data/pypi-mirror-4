from Products.BlingPortlet import BlingPortletMessageFactory as _
#from Products.BlingPortlet.vocabularies import changeVocabulary, orderingVocabulary
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from zope.configuration.fields import Path
from zope import schema
from zope.interface import Interface
from zope.configuration.fields import GlobalInterface

class IBaseBlingPortlet(IPortletDataProvider):
    name = schema.TextLine(
            title=_(u"label_bling_name_title", default=u"Title"),
            description=_(u"label_bling_name_description",
                          default=u"The title of the portlet."),
            default=u"",
            required=False)
    
    source = schema.Choice(
            title=_(u"label_bling_source_title", default=u"Bling Folder"),
            description=_(u'label_bling_source_description',
                          default=u"Search for and choose a Folder "
                                    "to act as the source of your bling."),
            required=True,
            source=SearchableTextSourceBinder({'is_folderish' : True},
                                              default_query='path:'))
    
    scale = schema.TextLine(
            title=_(u"label_bling_scale_title", default=u"Scale"),
            description=_(u"label_bling_scale_description",
                          default=u"The scale of the image to use."),
            default=u"thumb",
            required=False)
    
    links = schema.Bool(
            title=_(u"label_bling_links_title", default=u"Enable Links"),
            description=_(u"label_bling_links_description",
                          default=u"Check to enable linking from the displayed bling images"),
            default=True)
    
class IBlingPortlet(IBaseBlingPortlet):
    change = schema.Choice(
            title=_(u"label_bling_change_title", default=u"Change"),
            description=_(u"label_bling_change_description",
                          default=u"The frequency of change for the portlet."),
            vocabulary="Bling Changes",
            default=u"Random",
            required=True)
    
    view = schema.Choice(
        title=_(u"label_bling_view_title", default=u"View"),
        vocabulary="Bling Views",
        default="default",
        required=True)
    
class IBlingSlideshowPortlet(IBaseBlingPortlet):
    interval = schema.Int(
            title=_(u"label_bling_interval_title", default=u"Interval"),
            description=_(u"label_bling_interval_description",
                          default=u"The time between slides in milliseconds."),
            default=7000,
            min=0,
            required=True)
    
    ordering = schema.Choice(
            title=_(u"label_bling_ordering_title", default=u"Ordering"),
            description=_(u"label_bling_ordering_description",
                          default=u"The ordering of the slides."),
            vocabulary="Bling Orderings",
            default=u"Sequential",
            required=True)
    
    repeat = schema.Bool(
            title=_(u"label_bling_repeat_title", default=u"Repeat"),
            description=_(u"label_bling_repeat_description",
                          default=u"Check to enable repeating of the slideshow"),
            default=True)
    
    desc_limit = schema.Int(
            title=_(u"label_bling_description_limit_title", default=u"Description Length Limit"),
            description=_(u"label_bling_description_limit_description",
                          default=u"The maximum length of the description text before ellipsis (...) replace the remainder of the text."),
            default=16,
            min=0,
            required=False)
    
    view = schema.Choice(
        title=_(u"label_bling_view_title", default=u"View"),
        vocabulary="Bling Slideshow Views",
        default="default",
        required=True)
    
class IBlingImage(Interface):
    """Interface for Bling Images"""
    def getImage(scale=""):
        """URL of bling image at optional scale"""
    
    def getTitle():
        """title of bling image"""
        
    def getDescription():
        """description of bling image"""
        
    def getLink():
        """desired target link for bling image"""

class IBlingable(Interface):
    """Marker interface for content types that adapt to IBlingImage"""

class ILinkableImage(IBlingable):
    """Inteface for linkable images"""    
    
class IBlingView(Interface):
    name = schema.TextLine(
        title=u"Name",
        description=u"The name of the Bling view.",
        required=True
    )
    
    description = schema.TextLine(
        title=u"Description",
        description=u"The user-facing description of the Bling view.",
        required=False
    )
   
    template = Path(
        title=u"The name of a template that implements the page.",
        description=u"""
        Refers to a file containing a page template (should end in
        extension '.pt' or '.html').""",
        required=True
    )
    
    layer = GlobalInterface( 
        title=u"Layer", 
        description=u"The layer the view is registered against.", 
        required=False
    )        
    

class IBlingSlideshowView(Interface):
    name = schema.TextLine(
        title=u"Name",
        description=u"The name of the Bling view.",
        required=True
    )
    
    description = schema.TextLine(
        title=u"Description",
        description=u"The user-facing description of the Bling view.",
        required=False
    )
   
    template = Path(
        title=u"The name of a template that implements the page.",
        description=u"""
        Refers to a file containing a page template (should end in
        extension '.pt' or '.html').""",
        required=True
    )
    
    layer = GlobalInterface( 
        title=u"Layer", 
        description=u"The layer the view is registered against.", 
        required=False
    )        
    

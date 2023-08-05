from Products.BlingPortlet.interfaces import IBlingImage
from zope.interface import implements


class ImageToBling(object):
    """Adapter for fetching bling from ATImage objects"""
    implements(IBlingImage)
    
    def __init__(self, context):
        self.context = context
        
    def getImage(self, scale=''):
        if scale:
            return self.context.absolute_url() + '/image_' + scale
        return self.context.absolute_url()
    
    def getTitle(self):
        return self.context.Title()
    
    def getDescription(self):
        return self.context.Description()
    
    def getLink(self):
        return self.context.absolute_url() + "/view"

class NewsItemToBling(object):
    """Adapter for fetching bling from ATNewsItem objects"""
    implements(IBlingImage)
    
    def __init__(self, context):
        self.context = context
        
    def getImage(self, scale=''):
        imagefield = self.context.getImage()
        
        if imagefield == '':
            return u''
        if scale:
            return imagefield.absolute_url() + '_' + scale
        return imagefield.absolute_url()
    
    def getTitle(self):
        return self.context.Title()
    
    def getDescription(self):
        return self.context.Description()
    
    def getLink(self):
        return self.context.absolute_url()        
    
class LinkableImageToBling(object):
    """Adapter for fetching bling from LinkableImage objects"""    
    implements(IBlingImage)
    
    def __init__(self, context):
        self.context = context
        
    def getImage(self, scale=''):
        if scale:
            return self.context.absolute_url() + '/image_' + scale
        return self.context.absolute_url()
    
    def getTitle(self):
        return self.context.Title()
    
    def getDescription(self):
        return self.context.Description()
    
    def getLink(self):
        return self.context.getLink()

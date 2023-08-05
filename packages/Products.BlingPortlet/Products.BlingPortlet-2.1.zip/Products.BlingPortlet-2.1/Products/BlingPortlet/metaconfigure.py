from zope.component import getGlobalSiteManager
from zope.interface import implements
from Products.BlingPortlet.interfaces import IBlingView, IBlingSlideshowView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

def blingView(config, name, template, layer=None, description=None):
    if description is None:
        description = name
    gsm = getGlobalSiteManager()
    bvc = BlingViewClass(template, layer, description)
    gsm.registerUtility(bvc, IBlingView, name)
    
def blingSlideshowView(config, name, template, layer=None, description=None):
    if description is None:
        description = name
    gsm = getGlobalSiteManager()
    bvc = BlingSlideshowViewClass(template, layer, description)
    gsm.registerUtility(bvc, IBlingSlideshowView, name)
    
class BlingViewClass(object):
    implements(IBlingView)
    def __init__(self, template, layer, description):
        self.layer = layer
        self.template = ViewPageTemplateFile(template)        
        self.description = description        
        
class BlingSlideshowViewClass(object):
    implements(IBlingSlideshowView)
    def __init__(self, template, layer, description):
        self.layer = layer
        self.template = ViewPageTemplateFile(template)        
        self.description = description
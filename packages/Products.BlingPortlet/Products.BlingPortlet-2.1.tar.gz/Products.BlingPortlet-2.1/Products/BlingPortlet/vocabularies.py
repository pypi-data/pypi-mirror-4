from zope.component import getUtilitiesFor
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Products.BlingPortlet.interfaces import IBlingView, IBlingSlideshowView
from plone.browserlayer.utils import registered_layers

changeVocabulary = SimpleVocabulary([
                        SimpleVocabulary.createTerm(u'Random'),
                        SimpleVocabulary.createTerm(u'Each second'),
                        SimpleVocabulary.createTerm(u'Each minute'),
                        SimpleVocabulary.createTerm(u'Each hour'),
                        SimpleVocabulary.createTerm(u'Each day'),
                        SimpleVocabulary.createTerm(u'Each week'),
                        SimpleVocabulary.createTerm(u'Each month'),
                        SimpleVocabulary.createTerm(u'Each year')])
def blingChangeVocabulary(context):
    return changeVocabulary
alsoProvides(blingChangeVocabulary, IVocabularyFactory)

orderingVocabulary = SimpleVocabulary([
    SimpleVocabulary.createTerm(u'Random'),
    SimpleVocabulary.createTerm(u'Sequential')])
def blingOrderingVocabulary(context):
    return orderingVocabulary
alsoProvides(blingOrderingVocabulary, IVocabularyFactory)

def blingViewsVocabulary(context):
    utils = getUtilitiesFor(IBlingView)
    browser_layers = registered_layers()
    terms = [SimpleTerm(name, view.description) for name, view in utils if view.layer in browser_layers or view.layer is None]
    return SimpleVocabulary(terms)
alsoProvides(blingViewsVocabulary, IVocabularyFactory)

def blingSlideshowViewsVocabulary(context):
    utils = getUtilitiesFor(IBlingSlideshowView)
    browser_layers = registered_layers()
    terms = [SimpleTerm(name, view.description) for name, view in utils if view.layer in browser_layers or view.layer is None]
    return SimpleVocabulary(terms)
alsoProvides(blingSlideshowViewsVocabulary, IVocabularyFactory)
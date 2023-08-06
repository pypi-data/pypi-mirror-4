from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility 
from zope.schema.interfaces import IVocabularyFactory 
from zope.app.component.hooks import getSite
from zope.interface import alsoProvides 


#from zope.site.hooks import setSite


def ImageSizeVocabulary(object):
    return ['thumb', 'mini', 'preview', 'large', 'none']  
       
def format_size(size):
    return size.split(' ')[0]
    
def ImageSizesVocabulary(context):
    site = context.getSite()
    portal_properties = getToolByName(site, 'portal_properties', None)
    if 'imaging_properties' in portal_properties.objectIds():
        sizes = portal_properties.imaging_properties.getProperty(
        'allowed_sizes')
        terms = [SimpleTerm(value=format_size(pair),
            token=format_size(pair),
            title=pair) for pair in sizes]
    
        return SimpleVocabulary(terms)
    return ['thumb', 'mini', 'preview', 'large', 'none']  




 
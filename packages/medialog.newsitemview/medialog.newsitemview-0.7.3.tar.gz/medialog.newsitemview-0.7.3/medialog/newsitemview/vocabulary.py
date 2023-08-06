#from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
#from Products.CMFCore.utils import getToolByName
#from zope.component import getUtility 
#from zope.schema.interfaces import IVocabularyFactory 
from zope.app.component.hooks import getSite
#from zope.interface import alsoProvides 

#from five import grok
#from zope.schema.interfaces import IContextSourceBinder
#from zope.schema.vocabulary import SimpleVocabulary
#from Products.CMFCore.utils import getToolByName


def format_size(size):
    return size.split(' ')[0]
 


#@grok.provider(IContextSourceBinder)
#def ImageSizeVocabulary(self, context):
#    site = self.getSite()
#    sizes = ['thumb', 'thumb', 'mini', 'preview', 'large', 'none'] 
#    portal_properties = getToolByName(site, 'portal_properties', None)
#    if 'imaging_properties' in portal_properties.objectIds():
#        sizes = portal_properties.imaging_properties.getProperty(
#        'allowed_sizes')
#    terms = [SimpleTerm(value=format_size(pair),
#            token=format_size(pair),
#            title=pair) for pair in sizes]
#            
#    return SimpleVocabulary(terms)





 
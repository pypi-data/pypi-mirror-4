from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility 
from zope.schema.interfaces import IVocabularyFactory 
from zope.app.component.hooks import getSite
#from zope.site.hooks import setSite


def ImageSizeVocabulary(object):
    return ['thumb', 'mini', 'preview', 'large', 'none']  





        




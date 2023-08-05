from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from medialog.newsitemview import newsitemviewMessageFactory as _


class INewsItemView(Interface):
    """
    News Item view interface
    """

    def test():
        """ test method"""
        
    def imagesize():
        """ the image size used for news item view"""


class NewsItemView(BrowserView):
    """
    News Item browser view
    """
    implements(INewsItemView)
    
    def imagesize(self):
        try:
            size = self.context.newsitemsize
        except AttributeError:
            size = 'mini'           
        return size

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}

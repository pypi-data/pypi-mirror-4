from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from Products.Five import BrowserView
from collective.gsa.interfaces import IGSASchema


class AdvancedSearchURL(BrowserView):
    
    def __call__(self):
        
        registry = getUtility(IRegistry)
        config = registry.forInterface(IGSASchema)
        return config.advanced_search

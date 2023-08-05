from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from plone.app.layout.icons.interfaces import IContentIcon
from plone.app.layout.icons.icons import CatalogBrainContentIcon


class GSAFlareContentIcon(CatalogBrainContentIcon):
    implements(IContentIcon)
    
    @property
    def url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        path = self.brain.get('getIcon','document_icon.gif')
        return "%s/%s" % (portal_url, path)

    @property
    def description(self):
        return self.brain.Description

    @property
    def title(self):
        return None

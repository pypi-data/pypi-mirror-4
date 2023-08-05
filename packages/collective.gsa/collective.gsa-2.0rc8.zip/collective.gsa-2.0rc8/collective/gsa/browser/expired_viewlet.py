from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from plone.app.layout.viewlets import ViewletBase

class ExpiredViewlet(ViewletBase):
    
    render = ViewPageTemplateFile("expired_viewlet.pt")
    
    def available(self):
        mtool = getMultiAdapter( (self.context, self.request), name=u"plone_tools").membership()
        return not mtool.isAnonymousUser() and 'GSACookie' not in self.request.cookies
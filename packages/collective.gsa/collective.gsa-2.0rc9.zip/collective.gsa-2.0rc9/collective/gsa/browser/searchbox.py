from zope.component import getMultiAdapter

from plone.app.layout.viewlets.common import ViewletBase

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class SearchBoxViewlet(ViewletBase):
    index = ViewPageTemplateFile('searchbox.pt')

    def render(self):
        return self.index()

    def update(self):
        super(SearchBoxViewlet, self).update()

        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        props = getToolByName(self.context, 'portal_properties')
        livesearch = props.site_properties.getProperty('enable_livesearch', False)
        if livesearch:
            self.search_input_id = "searchGadget"
        else:
            self.search_input_id = ""

        
        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())

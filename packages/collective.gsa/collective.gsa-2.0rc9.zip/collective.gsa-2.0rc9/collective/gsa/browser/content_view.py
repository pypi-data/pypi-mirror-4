from zope.component import getMultiAdapter
from zope.interface import implements, Interface

from Products.Five import BrowserView

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

def _getContext(self):
    while 1:
        self = self.aq_parent
        if not getattr(self, '_is_wrapperish', None):
            return self


class IContentView(Interface):
    """ Provides content to be pushed to GSA
    """

        
class ContentView(BrowserView):
    """ Provides content to be pushed to GSA
    """
    
    implements(IContentView)
    
    template = ViewPageTemplateFile('content_view.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

        ZopeTwoPageTemplateFile._getContext = _getContext

    def getDefaultTemplate(self):            
        template = getattr(self.context, self.context.getLayout(), None)
        
        if not template:
            fti = self.context.getTypeInfo()
            view_method_name = fti.getViewMethod(self.context)

            view_method = self.context.restrictedTraverse(view_method_name)

            if hasattr(view_method, 'template'):
                template = view_method.template.__of__(self.context)
            elif hasattr(view_method, 'index'):
                template = view_method.index.__of__(self.context)
            else:
                template = view_method
                
        return template

    def __call__(self):
        def_page = self.context.getDefaultPage()
        
        if def_page:
            context = self.context[def_page]
            view = getMultiAdapter(( context, self.request), name=u"gsa-contentview")
            return view()
        
        return self.template()
                    
    

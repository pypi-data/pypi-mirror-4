import base64

from zope.interface import implements
from zope.component import getMultiAdapter

from collective.gsa.utils import safe_unicode
from collective.gsa.interfaces import IContentProvider



class BaseContentProvider(object):
    """ Provides content to be pushed to GSA
    """
    
    implements(IContentProvider)
    
    def __init__(self, context, request = None):
        self.context = context
        self.request = request

    def content(self):
        title = self.context.Title()
        description = self.context.Description()
        content = u"%s - %s" % (safe_unicode(title), safe_unicode(description))
        return content, None

class DefaultContentProvider(object):
    """ Provides content to be pushed to GSA
    """

    implements(IContentProvider)

    def __init__(self, context, request = None):
        self.context = context
        self.request = request

    def content(self):
        if self.context.getLayout():
            content_html = self.context()
            content = u"<![CDATA[%s]]>" % content_html
        else:
            title = self.context.Title()
            description = self.context.Description()
            content = u"%s - %s" % (safe_unicode(title), safe_unicode(description))

        return content, None
        
class FileContentProvider(object):
    """ Provides content to be pushed to GSA
    """

    implements(IContentProvider)

    def __init__(self, context, request = None):
        self.context = context
        self.request = request

    def content(self):
        data = self.context.get_data()
        content = base64.b64encode(data)
        encoding = "base64binary"
        return content, encoding

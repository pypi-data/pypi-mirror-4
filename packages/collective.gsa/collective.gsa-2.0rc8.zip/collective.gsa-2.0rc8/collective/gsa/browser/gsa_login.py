from zope.component import getUtility

from Products.Five import BrowserView

from collective.gsa.interfaces import IGSAConnectionManager


class GSALogin(BrowserView):
    
    def __call__(self):
        manager = getUtility(IGSAConnectionManager)
        conn = manager.getSearchConnection(self.request)
        if conn:
            conn.login(self.request['__ac_name'], self.request['__ac_password'])

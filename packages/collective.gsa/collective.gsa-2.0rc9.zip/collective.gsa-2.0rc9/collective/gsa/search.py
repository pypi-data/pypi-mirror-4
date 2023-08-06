from logging import getLogger
from zope.interface import implements
from zope.component import queryUtility, getUtility
from plone.registry.interfaces import IRegistry

from collective.gsa.interfaces import IGSASchema
from collective.gsa.interfaces import IGSAConnectionManager
from collective.gsa.interfaces import ISearch
from collective.gsa.parser import GSAResponse
from collective.gsa.exceptions import GSAUnreachableException
from collective.gsa.utils import safe_unicode

logger = getLogger('collective.gsa.search')

GSA_TAGS = {
    u'SearchableText':u'q',
    u'site':u'site',
    u'client':u'client',
    u'rows':u'num',
#    u'path':u'as_sitesearch',
}

class Search(object):
    """ a search utility for gsa """
    implements(ISearch)

    def __init__(self):
        self.manager = None
        self.isAnon = True

    def getManager(self):
        if self.manager is None:
            self.manager = queryUtility(IGSAConnectionManager)
        return self.manager

    def search(self, context, query, **parameters):
        """ perform a search with the given querystring and parameters """
        manager = self.getManager()
        connection = manager.getSearchConnection(self.request)
        if connection is None:
            raise GSAUnreachableException

        registry = getUtility(IRegistry)
        config = registry.forInterface(IGSASchema)
        if not parameters.has_key('rows'):
            parameters['rows'] = config.max_results or ''

        response, error = connection.search(q=query, **parameters)
        if error == 401:
            logger.info('GSA cookie expired. Returning public results')
            # If we needed to notify user when that happened - note the portalMessage has to be called explicitely after search is called
            #IStatusMessage(context.REQUEST).addStatusMessage("GSA cookie has expired. Only public items are searchable.","warning")
            
            ## We got unauthorized => we have a cookie but a wrong one -> invalidate it
            connection.invalidateCookie()
            # and repeat
            response, error = connection.search(q=query, **parameters)
            
        return GSAResponse().parse(context,response)

    __call__ = search

    def buildQuery(self, default=None, **args):
        """ helper to build a querystring for simple use-cases """
        logger.debug('building query for "%r", %r', default, args)
        prepare_query = []
        for arg, val in args.items():
            if val and arg in GSA_TAGS.keys():
                prepare_query.append(u"%s=%s" % (GSA_TAGS[arg],safe_unicode(val)))
                
        query = "&".join(prepare_query)
        return query
        
    def setRequest(self, request):
        self.request = request

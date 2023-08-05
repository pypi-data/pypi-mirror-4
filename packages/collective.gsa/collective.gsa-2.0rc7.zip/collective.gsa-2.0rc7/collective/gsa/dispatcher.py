from zope.interface import implements
from zope.component import queryUtility, queryMultiAdapter, getSiteManager, \
        getUtility
from zope.publisher.interfaces.http import IHTTPRequest
from Products.ZCatalog.ZCatalog import ZCatalog
from plone.registry.interfaces import IRegistry

from collective.gsa.interfaces import IGSASchema
from collective.gsa.interfaces import ISearchDispatcher
from collective.gsa.interfaces import ISearch
from collective.gsa.interfaces import IFlare

from collective.gsa.utils import isActive, isAnonymous

class FallBackException(Exception):
    """ exception indicating the dispatcher should fall back to searching
        the portal catalog """


class SearchDispatcher(object):
    """ adapter for potentially dispatching a given query to an
        alternative search backend (instead of the portal catalog) """
    implements(ISearchDispatcher)

    def __init__(self, context):
        self.context = context        

    def __call__(self, request, **keywords):
        """ decide on a search backend and perform the given query """
        if self.useGSA(**keywords) and isActive():
            try:
                return gsaSearchResults(self.context, request, **keywords)
            except FallBackException:
                pass
        return ZCatalog.searchResults(self.context, request, **keywords)

    def useGSA(self, **keywords):
        return keywords.has_key('gsasearch')

def gsaSearchResults(context, request=None, **keywords):
    """ perform a query using solr after translating the passed in
        parameters with portal catalog semantics """

    search = queryUtility(ISearch)
    registry = getUtility(IRegistry)
    config = registry.forInterface(IGSASchema)
    if request is None:
        # try to get a request instance, so that flares can be adapted to
        # ploneflares and urls can be converted into absolute ones etc;
        # however, in this case any arguments from the request are ignored
        request = getattr(getSiteManager(), 'REQUEST', None)
        args = keywords
    elif IHTTPRequest.providedBy(request):
        args = request.form.copy()  # ignore headers and other stuff
        args.update(keywords)       # keywords take precedence
    else:
        assert isinstance(request, dict), request
        args = request.copy()
        args.update(keywords)       # keywords take precedence
    
    if args.get('path'):
        args['path'] = request.physicalPathToURL(args['path'])

    args['site'] = config.site
    if config.dual_collection and isAnonymous(context):
        args['site'] = config.dual_collection
        
    args['client'] = config.client
    args['rows'] = keywords.get('rows',0) or config.max_results
    
    # get credentials
    # not used anymore
    #acl_users = getToolByName(context, 'acl_users')
    #extractor = getMultiAdapter( (acl_users, request) )
    #credentials = extractor.extractCredentials()
    search.setRequest(request)    
    query = search.buildQuery(**args)
    results = search(context, query)
    def wrap(flare):
        """ wrap a flare object with a helper class """
        adapter = queryMultiAdapter((flare, request), IFlare)
        return adapter is not None and adapter or flare
    return map(wrap, results)
    

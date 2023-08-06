from zope.interface import Interface
from zope.schema import Bool, TextLine, Int, Float
from zope.viewlet.interfaces import IViewletManager


from collective.gsa import GSAMessageFactory as _

class IGSASchema(Interface):

    active = Bool(title=_(u'Active'), default=False,
        description=_(u'Check this to enable the GSA integration, i.e. '
                       'indexing and searching using the below settings.'))

    host = TextLine(title=_(u'Host'),
        description=_(u'The host name of the GSA instance to be used.'))

    client = TextLine(title=_(u'Front-end'),
        description=_(u'GSA front-end (client) to use for searching'))
    
    port_index = Int(title=_(u'Port for indexing'),
        description=_(u'The port of the GSA indexing server.'))

    port_psearch = Int(title=_(u'Port for public searching'),
        description=_(u'The port of the GSA public searching server.'))

    port_ssearch = Int(title=_(u'Port for secure searching'),
        description=_(u'The port of the GSA secure searching server.'))

    only_public = Bool(title=_(u'Only public search'),
        description=_(u'Search only public content.'))

    public_search = Bool(title=_(u'Secure public search'),
        description=_(u'Check to use secure connection for public search. This needs to follow GSA settings.'))

    secure_search = Bool(title=_(u'Secure secure search'),
        description=_(u'Check to use secure connection for secure search. This needs to follow GSA settings.'))

    source = TextLine(title=_(u'Source'),
        description=_(u'The data source for xmlfeed'))
        
    site = TextLine(title=_(u'The GSA collection to use for secure searching'),
        description=_(u'The primary collection the authenticated users search in.'),
        default = u'default_collection')

    dual_site = TextLine(title=_(u'The base url of a dual site'),
                    description=_(u'This is useful when you have different base url for anonymous access.'),
                    required=False)

    dual_collection = TextLine(title=_(u'The GSA colletion to use for anonymous searching'),
                            description=_(u'For dual search, you can have a different collection.'),
                            required = False)

    max_results = Int(title=_(u'Maximum search results'),
        description=_(u'Specify the maximum number of matches to be returned when '
                       'searching.  Set to "0" to always return all results.'))

    advanced_search = TextLine(title=_(u'URL of a GSA advanced search'),
                           description=_(u'If an url is entered there would be a link to it at the top of the search page.'),
                           required = False)

    feed_path = TextLine(title=_(u'A temporary directory for the xml feeds'),
        description=_(u'Enter a directory where the xml feed are store before the'\
                      'sender would process them'),
                         required = True)

    timeout = Float(title=_(u'A connection timeout'),
               description=_(u'Specify a connaction timeout to use for search.'\
                             'if left empty the system default will be used'),
                   required = False)

                       

class IGSAConnectionConfig(IGSASchema):
    """ utility to hold the connection configuration for the gsa server """


class IGSAConnectionManager(Interface):
    """ a thread-local connection manager for gsa """


class IGSAFlare(Interface):
    """ a gsa brain, i.e. a data container for search results """


class IFlare(Interface):
    """ marker interface for pluggable brain wrapper classes, providing
        additional helper methods like `getURL` etc """


class ISearch(Interface):
    """ a generic search interface
        FIXME: this should be defined in a generic package """

    def search(query, **parameters):
        """ perform a search with the given querystring and extra parameters"""

    def __call__(query, **parameters):
        """ convenience alias for `search` """

    def buildQuery(default=None, **args):
        """ helper to build a querystring for simple use-cases """


class ICatalogTool(Interface):
    """ marker interface for plone's catalog tool """

class ISearchDispatcher(Interface):
    """ adapter for potentially dispatching a given query to an
        alternative search backend (instead of the portal catalog) """

    def __call__(request, **keywords):
        """ decide if an alternative search backend is capable of performing
            the given query and use it or fall back to the portal catalog """

class IContentProvider(Interface):
    """ adapter for retreiving content from an object 
        
        see content_provider.py on how to create adapters for own content types
    """
    
    def content():
        """ Retreive data from object 
            returns data and encoding if neccessary
            
            if the data are text/html it has to be wrapped by <![CDATA[%s]]>
        """
    
class IGSAQueue(Interface):
    """ Local utility to saved unprocessed feeds """
    
class IGSAViewletManager(IViewletManager):
    """A viewlet manager that sits in the <head> of the rendered page
    """

class IGSAFeedGenerator(Interface):
    """ Interface of an adapter to produce gsa feed """

from logging import getLogger

from zope.interface import implements
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from collective.gsa.interfaces import IGSASchema
from collective.gsa.interfaces import IGSAConnectionManager
from collective.gsa.gsa import GSAConnection
from collective.gsa.local import getLocal, setLocal

logger = getLogger('collective.gsa.manager')
marker = object()


class GSAConnectionManager(object):
    implements(IGSAConnectionManager)

    def getSearchConnection(self, request, timeout=marker):
        isAnon = not request.cookies.get('GSACookie') and not request.get('__ac_name')
        registry = getUtility(IRegistry)
        config = registry.forInterface(IGSASchema)
        if not config:
            logger.error('Cannot resolve connection config. Not searching')
            return None
        if not config.active:
            return None
        if config.host is not None:
            # if anonym search decide using public search config otherwise secure_search
            if isAnon:
                secure = config.public_search
            else:
                secure = config.secure_search

            port = secure and config.port_ssearch or config.port_psearch
            conn_string = 'search_connection_%s_%s' % (secure, port)

            conn = getLocal(conn_string)
            if conn is None:
                conn = GSAConnection(host=config.host, port = port,
                                     source=config.source, secure=secure,
                                     only_public = config.only_public,
                                     request = request, timeout=config.timeout)
                setLocal(conn_string, conn)

        return conn

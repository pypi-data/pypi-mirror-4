import os
import time
from logging import getLogger
import re
import urllib
from ZODB.POSException import ConflictError

from zope.app.component.hooks import getSite
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from plone.app.content.interfaces import IIndexableObjectWrapper
from collective.gsa.interfaces import IContentProvider, IGSASchema
from zope.component import queryMultiAdapter, getUtility
from collective.gsa.utils import safe_unicode
from zope.interface import implements
from collective.gsa.interfaces import IGSAFeedGenerator
from xml.sax.saxutils import escape

logger = getLogger('collective.gsa.indexer')
BADCHAR_PATTERN = re.compile('[\x00-\x08\x11\x12\x14-\x19]')

XML_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE gsafeed PUBLIC "-//Google//DTD GSA Feeds//EN" "">
<gsafeed>
    <header>
        <datasource>%s</datasource>
        <feedtype>incremental</feedtype>
    </header>
    <group>%s</group>
</gsafeed>
"""

class Indexer(object):
    implements(IGSAFeedGenerator)
    
    def __init__(self, context):
        self.context = context
        registry = getUtility(IRegistry)
        self.config = registry.forInterface(IGSASchema)
        self.path = self.config.feed_path

        if not os.path.exists(self.path):
            os.makedirs(self.path)
    
    def process(self, action):
        if not self.config.active:
            return

        # Handle the search filter
        portal = getSite()
        plone_utils = getToolByName(portal, 'plone_utils')
        
        portal_type = getattr(self.context, 'portal_type', None)
        if portal_type and portal_type not in plone_utils.getUserFriendlyTypes():
            return
        
        if action == "add":
            xml = self._prepareAdd()
            logger.info("Logging adding of %s" % self.context.absolute_url())
        elif action == "delete":
            xml = self._prepareDelete()
            logger.info("Logging deleting of %s" % self.context.absolute_url())
        else:
            logger.error("Unknown process type: has to be one of: add, delete")
            return
        
        self.save(xml)

    def save(self, xml):
        if hasattr(self.context, 'UID'):
            uid = self.context.UID()
        else:
            uid = self.context.getId()

        filename = "%s-%s.gsa" % (uid, time.time())
        fullname = os.path.join(self.path, filename)

        lock_file = "%s.lock" % fullname

        try:
            open(lock_file, 'w').close()
            handle = open(fullname, 'w')
            handle.write(xml.encode('utf-8'))
            handle.close()
        finally:
            if os.path.exists(lock_file):
                os.remove(lock_file)
            
    def _prepareAdd(self):
        data = self._prepareData()
        row_dict = dict(
            url = urllib.unquote(data['url']),
            path = urllib.unquote(data['path']),
            action = u'add',
            mimetype = data['mimetype'],
            modified = data['last-modified'],
            content = (data['content'], data.get('content_encoding')),
            metadata = data['metadata']
        )

        if data.get('authmethod'):
            row_dict['authmethod'] = data['authmethod']

        xml = self._getRecordXML(row_dict)
        if self.config.dual_site:
            xml += self._getRecordXML(row_dict, dual=True)
            
        return self._finalizeXML(xml)

    def _prepareDelete(self):
        obj = self.context
        row_dict = dict(
            url = obj.absolute_url(),
            path = obj.absolute_url_path(),
            action = u'delete'
        )
        xml = self._getRecordXML(row_dict)
        if self.config.dual_site:
            xml += self._getRecordXML(row_dict, dual=True)
            
        return self._finalizeXML(xml)
        
    def _prepareData(self):
        obj = self.context
        
        data = {}
        data['url'] = obj.absolute_url()
        data['path'] = obj.absolute_url_path()
        data['last-modified'] = obj.modified().rfc822()
        data['mimetype'] = obj.Format()
        cnt_provider = queryMultiAdapter((obj, obj.REQUEST), IContentProvider)

        data['content'] = None
        if cnt_provider:
            try:
                data['content'], data['content_encoding'] = cnt_provider.content()
            except ConflictError, e:
                raise
            except Exception, e:
                logger.warning('Could not get the object\'s content. Reason: %s' % e)
                raise

        if data['content'] is None:
            data['content'] = u"%s - %s" % (safe_unicode(obj.Title()), safe_unicode(obj.Description()))
            data['content_encoding'] = None

        # Check the content validity
        badcharresults = BADCHAR_PATTERN.search(data['content'])
        if badcharresults:
            logger.debug('reindexing BAD CHARACTERS url: %s, content: %s' % (data['url'],repr(data['content'][badcharresults.start()-20:badcharresults.start()+20])))        
            return None

        # If anonymous has View access, omit the authmethod tag
        pms = obj.permissionsOfRole('Anonymous')
        view_pm = [x for x in pms if x['name'] == 'View']
        if len(view_pm) > 0 and view_pm[0]['selected']:
            data['authmethod'] = "none"
        else:
            data['authmethod'] = "httpbasic"

        mt_data = {}
        catalog = getToolByName(obj, 'portal_catalog')
        schema = catalog.schema()
        wr_obj = self._wrapObject(obj)
        for meta in schema:
            val = getattr(wr_obj, meta, None)
            if callable(val):
                val = val()
            if val:
                mt_data[meta] = val

        data['metadata'] = mt_data
        return data

    def _wrapObject(self, obj):
        """ wrap object with an "IndexableObjectWrapper`, see
            `CatalogTool.catalog_object` for some background """
        portal = getToolByName(obj, 'portal_url', None)
        if portal is None:
            return obj
        portal = portal.getPortalObject()
        wrapper = queryMultiAdapter((obj, portal), IIndexableObjectWrapper)
        if wrapper is None:
            return obj
        wft = getToolByName(obj, 'portal_workflow', None)
        if wft is not None:
            wrapper.update(wft.getCatalogVariablesFor(obj))
        return wrapper
        
    def _getRecordXML(self, row, dual = False):
        # unicodize to be sure
        row = self._unicodize(row)
        url = row['url']
        if dual:
            url = "%s%s" % (self.config.dual_site,row['path'])

        if row['action'] == 'delete':
            txt = u"<record url=\"%s\" action=\"%s\" mimetype=\"\" />" % (url, row['action'])
            return txt

        txt = u"<record url=\"%s\" action=\"%s\" mimetype=\"%s\" last-modified=\"%s\" authmethod=\"%s\">" \
                % (url, row['action'], row['mimetype'], row['modified'], row['authmethod'])
        mt_data = row.get('metadata',{})
        if mt_data:
            txt += u"<metadata>"
            for name, value in mt_data.items():
                txt += u"<meta name=\"%s\" content=\"%s\"/>" % (safe_unicode(name), escape(safe_unicode(value), {'"':'&quot;'}))
            txt += u"</metadata>"
        content = row.get('content')
        if content:
            enc = content[1] and u"encoding=\"%s\"" % safe_unicode(content[1]) or u""
            cnt = content[0].startswith('<![CDATA') and safe_unicode(content[0]) or escape(safe_unicode(content[0]), {'"':'&quot;'})
            txt += u"<content %s>%s</content>" % (enc, cnt)
        txt += u"</record>"
        return txt
    
    def _finalizeXML(self, value):
        xml = XML_TEMPLATE % (self.config.source.encode('utf-8'),value)
        return xml
    
    def _unicodize(self, val):
        if isinstance(val, str):
            data = safe_unicode(val)
        elif isinstance(val, (list,tuple,set)):
            data = []
            for item in val:
                data.append(self._unicodize(item))
        elif isinstance(val, dict):
            data = val
            for k, v in val.iteritems():
                data[k] = self._unicodize(v)
        else:
            data = val
                
        return data

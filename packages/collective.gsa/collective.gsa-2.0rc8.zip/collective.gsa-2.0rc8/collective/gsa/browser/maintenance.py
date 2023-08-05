from collective.gsa.interfaces import IGSAFeedGenerator
import gc
import transaction
from logging import getLogger
from plone.memoize import view
from zope.component import getUtility, getMultiAdapter

from collective.gsa.interfaces import IGSAQueue

from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

logger = getLogger('collective.gsa.maintenance')


class GSAMaintenance(BrowserView):

    _template = ViewPageTemplateFile('maintenance.pt')
    
    def __call__(self):
        annotations = IAnnotations(self.context)
        self.data = annotations.setdefault('gsa.reindex.batching', PersistentDict())
        putils = getToolByName(self.context, 'plone_utils')
        if self.request.has_key('collective.gsa.startover'):
            self.data['start'] = 0
            
        elif self.request.has_key('collective.gsa.reindex'):
            batch_size = self.request.get('batch_size', 5000)
            start = self.data.get('start', 0)
            end = start + int(batch_size)
                        
            logger.info('Reindexing started start: %s, stop:%s' % (start,end))

            brains = self.brains()
            walker = self.walk(brains, start, end)
            count = self.count()
            
            i = int(start)
            for obj in walker:
                if i % 5 == 0:
                    logger.info('Reindexing: %d out of %s' % (i,count))
                
                IGSAFeedGenerator(obj).process("add")    
                i += 1
                    
        return self._template()
    
    def progress(self):
        return self.data.get('start', 0)
        
    @view.memoize
    def brains(self, path = None):
        if not path:
            path = '/'.join(self.context.getPhysicalPath())
        
        catalog = getMultiAdapter( (self.context, self.request), name=u"plone_tools").catalog()
        return catalog.searchResults(path = path)

    @view.memoize
    def count(self):
        return len(self.brains())

    def walk(self, brains, start = 0, end = None):
        finish = True
        for cnt, brain in enumerate(brains):
            if cnt < start:
                continue
            if end and cnt >= end:
                self.data['start'] = end
                finish = False
                break
                
            obj = brain.getObject()
            if obj is not None:
                yield obj
        
        if finish:        
            self.data['start'] = self.count()
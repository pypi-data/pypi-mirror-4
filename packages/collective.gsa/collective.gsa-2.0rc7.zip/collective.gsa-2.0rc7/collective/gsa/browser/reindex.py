from logging import getLogger
from Products.Five import BrowserView

from collective.gsa.interfaces import IGSAFeedGenerator

logger = getLogger('collective.gsa.indexing')

class Reindex(BrowserView):
    
    def __call__(self):
        processor = IGSAFeedGenerator(self.context)
        processor.process(action="add")
        return

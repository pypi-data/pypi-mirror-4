from logging import getLogger
from collective.gsa.interfaces import IGSAFeedGenerator
from collective.gsa.utils import gsa_installed

from zope.lifecycleevent import ObjectMovedEvent
from collective.gsa.monkey import patchCatalogTool
patchCatalogTool()      # patch catalog tool to use the dispatcher...

logger = getLogger('collective.gsa.indexer')

class DeletedObject(object):
    """ A dummy object for deleting """

    def __init__(self, url, path, uid):
        self.url = url
        self.path = path
        self.uid = uid

    def absolute_url(self):
        return self.url

    def absolute_url_path(self):
        return self.path

    def UID(self):
        return "%s-remove" % self.uid

def GSALogout(user, event):
    user.REQUEST.RESPONSE.expireCookie('GSACookie')


def GSAAdded(obj, event):
    if not gsa_installed():
        return
    if obj.isTemporary() or obj.checkCreationFlag():
        return
    logger.debug("Added: %s" % event.__class__)
    processor = IGSAFeedGenerator(obj)
    processor.process(action="add")

def GSARemoved(obj, event):
    if not gsa_installed():
        return

    request = obj.REQUEST
    # if it's delete confirmation check it's been submitted
    if 'delete_confirmation' in request['URL']:
        if not request.get('form.submitted'):
            return
    
    logger.debug("Removed: %s" % event.__class__)
    processor = IGSAFeedGenerator(obj)
    processor.process(action="delete")
    
def GSAMoved(obj, event):
    if not gsa_installed():
        return

    if obj.isTemporary() or obj.checkCreationFlag():
        return

    if event.__class__ != ObjectMovedEvent:
        return

    logger.debug("Moved: %s" % event.__class__)
    try:
        if event.oldParent and event.oldName:
            url = obj.absolute_url()
            path = obj.absolute_url_path()

            if event.newParent:
                old_parent_path = event.oldParent.absolute_url_path() + "/" \
                                        + event.oldName
                new_parent_path = event.newParent.absolute_url_path() + "/" \
                                        + event.newName
                url = url.replace(new_parent_path, old_parent_path)
                path = path.replace(new_parent_path, old_parent_path)
            else:
                url = event.oldParent.absolute_url() + "/" + event.oldName
                path = event.oldParent.absolute_url_path() + "/" + event.oldName

            old = DeletedObject(url=url, path=path, uid=obj.UID())
            processor = IGSAFeedGenerator(old)
            processor.process(action="delete")

        if event.newName:
            processor = IGSAFeedGenerator(obj)
            processor.process(action="add")
    except Exception, e:
        logger.error(e)
        raise

def GSAWorkflowChanged(obj, event):
    if not gsa_installed():
        return
    
    try:
        processor = IGSAFeedGenerator(obj)
        processor.process(action="add")
    except Exception, e:
        logger.error(e)
        raise

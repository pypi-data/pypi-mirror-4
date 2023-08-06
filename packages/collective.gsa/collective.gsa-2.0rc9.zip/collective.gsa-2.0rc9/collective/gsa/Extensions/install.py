from Products.CMFCore.utils import getToolByName

from collective.gsa.interfaces import IGSAConnectionConfig
from collective.gsa.interfaces import IGSAConnectionManager
from collective.gsa.interfaces import IGSAQueue

UTILS = [
    IGSAQueue,
    IGSAConnectionConfig,
    IGSAConnectionManager,
]

def install(portal, reinstall=False):
    print "Instaling"
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.gsa:default')
    return "Ran all import steps."

def uninstall(portal):
    sm = portal.getSiteManager()
    print "Uninstalling"
    for util in UTILS:
        ut_obj = sm.queryUtility(util)
        if ut_obj is not None:
            sm.unregisterUtility(provided=util)
            del ut_obj
        
        sm.utilities.unsubscribe((), util)
        
        try:
            del sm.utilities.__dict__['_provided'][util]
        except KeyError:
            pass

        try:
            del sm.utilities._subscribers[0][util]
        except KeyError:
            pass

        
    sm.utilities._p_changed = True
        

    return "Ran all uninstall steps."
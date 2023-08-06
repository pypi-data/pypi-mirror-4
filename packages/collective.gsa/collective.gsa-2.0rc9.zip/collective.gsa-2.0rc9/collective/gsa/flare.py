import re

from ZODB.POSException import ConflictError

from zope.interface import implements
from zope.component import adapts, getSiteManager
from zope.publisher.interfaces.http import IHTTPRequest
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

from collective.gsa.interfaces import IGSAFlare
from collective.gsa.interfaces import IFlare
from collective.gsa.parser import AttrDict
from collective.gsa.exceptions import GSAFlareNotObjectableException
timezone = DateTime().timezone()


class PloneFlare(AttrDict):
    """ a sol(a)r brain, i.e. a data container for search results """
    implements(IFlare)
    adapts(IGSAFlare, IHTTPRequest)

    __allow_access_to_unprotected_subobjects__ = True

    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        self.update(context.__dict__)  # copy data
        self.subre = re.compile("'(.+?)'")
        self.keymatch = self.get('GD', False)
        

    @property
    def id(self):
        """ convenience alias """
        return self.get('id', self.get('getId'))

    def Title(self):
        if self.keymatch:
            return self.get('GD','')
        else:
            return self.get('T') or self.get('U', '')
        
    @property
    def Description(self):
        return self.get('S','')
    
    def Subject(self):
        
        result = None
        subject = self.get('Subject',None)
        if subject:
            result = self.subre.findall(subject)
        return result
        
    def getURL(self):
        if self.keymatch:
            return self.get('GL','')
        else:
            return self.get('U' ,'')
        
    def getPath(self):
        """ convenience alias """
        return self.request.physicalPathFromURL(self.getURL())

    @property
    def Creator(self):
        creator = self.get('Creator')
        if creator:
            membership = getToolByName(self.context.context,'portal_membership')
            user = membership.getMemberById(creator)
            if user:
                return creator
                
    def getObject(self, REQUEST=None):
        """ return the actual object corresponding to this flare """
        site = getSiteManager()
        
        try:
            path = self.getPath()
            obj = site.unrestrictedTraverse(path)
        except ConflictError, e:
            raise
        except Exception, e:
            raise GSAFlareNotObjectableException, e

        return obj

    def isLocal(self):
        """ Returns true if the url matches virtual host setting"""
        try:
            self.getPath()
        except ValueError, e:
            return False
        return True
        
    def pretty_title_or_id(self):
        for attr in 'Title', 'getId', 'id':
            atr = None
            if self.has_key(attr):
                if self[attr]:
                    atr = self[attr]
            if hasattr(self,attr):
                atr = getattr(self,attr)
                if callable(atr):
                    atr = atr()
            if atr:
                return atr
        return '<untitled item>'
        
    @property
    def data_record_normalized_score_(self):
        rank = ''
        try:
            rank = int(float(self['RK']) * 10)
        except:
            pass
            
        return rank

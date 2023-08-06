import codecs
import urllib
import urllib2
import mechanize
import base64
import os
from xml.sax.saxutils import escape

from AccessControl import Unauthorized
from zope.component import getUtility

from collective.gsa.utils import encode_multipart_formdata, safe_unicode, make_cookie
from collective.gsa.config import LIMIT
from logging import getLogger


logger = getLogger(__name__)

debug = False

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

class GSAException(Exception):
    """ An exception thrown by gsa connections """

    def __init__(self, httpcode, reason=None, body=None):
        self.httpcode = httpcode
        self.reason = reason
        self.body = body

    def __repr__(self):
        return 'HTTP code=%s, Reason=%s, body=%s' % (
                    self.httpcode, self.reason, self.body)

    def __str__(self):
        return 'HTTP code=%s, reason=%s' % (self.httpcode, self.reason)


class GSAConnection:

    def __init__(self, host='', port = None, source = '', postHeaders={},
                secure = False, timeout = None, only_public = False,
                 request = None, dual_site = None):
        self.host = host
        self.port = port
        self.source = source
        self.encoder = codecs.getencoder('utf-8')
        self.timeout = timeout
        self.only_public = only_public
        self.dual_site = dual_site
        # responses from GSA will always be in UTF-8
        self.decoder = codecs.getdecoder('utf-8')  
        #self.toindex = {}
        self.xmlbody = []
        self.xmlheaders = {}
        self.xmlheaders.update(postHeaders)
        self.request = request
        # Prepare connection
        if secure:
            self.url = "https://%s:%s" % (host, port)
        else:
            self.url = "http://%s:%s" % (host, port)
        
    def __str__(self):
        return 'GSAConnection{host=%s, postHeaders=%s}' % \
            (self.host, self.xmlheaders)

    def login(self, username, password):
        """ Log into GSA and store GSA credential cookie 
        """
        logger.debug('Logging in')
        password_mgr = mechanize.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.url, username, password)
        
        cj = mechanize.CookieJar()
        cookie_handler = mechanize.HTTPCookieProcessor(cj)
                
        if debug:
            opener = mechanize.build_opener(cookie_handler, mechanize.HTTPHandler(debuglevel=1), mechanize.HTTPSHandler(debuglevel=1))
        else:
            opener = mechanize.build_opener(cookie_handler)
            
        req = mechanize.Request('%s/search?access=a' % self.encoder(self.url)[0])
        if self.timeout:
            req.timeout = self.timeout
        base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
        req.add_header("Authorization", "Basic %s" % base64string)

        try:
            res = opener.open(req)
        except urllib2.HTTPError, e:
            logger.warning('Login failed. The server couldn\'t fulfill the request. Error code: %s' % e.code)
            self.request.response.setCookie('GSACookie', base64.b64encode('Unauthorized'))
            
        except urllib2.URLError, e:
            logger.warning('Login failed. We failed to reach a server. Reason: %s ' % e.reason)
        else:
            # get the cookie
            self.saveCookies(cj)
            res.close()

    def saveCookies(self,cj):
        cookie_ids = [x for x in cj if x.name == 'GSA_SESSION_ID']
        if len(cookie_ids) == 1:
            cookie = cookie_ids[0]
            cookie_str = mechanize.lwp_cookie_str(cookie)
            self.request.response.setCookie('GSACookie', base64.b64encode(cookie_str))

        cookie_ids = [x for x in cj if x.name == 'JSESSION_ID']
        if len(cookie_ids) == 1:
            cookie = cookie_ids[0]
            cookie_str = mechanize.lwp_cookie_str(cookie)
            self.request.response.setCookie('GSACookie2', base64.b64encode(cookie_str))
        

    def getCredentialsCookie(self, cookie_name = 'GSACookie'):
        cookie = None
        try:
            cookie_str = base64.b64decode(self.request.cookies.get(cookie_name,''))
            cookie = make_cookie(cookie_str)
        except AttributeError:
            pass
            
        return cookie

    def invalidateCookie(self, cookie_name = 'GSACookie'):
        self.request.response.expireCookie('GSACookie')
        if self.request.cookies.has_key('GSACookie'):
            del self.request.cookies['GSACookie']
        
    def __errcheck(self,rsp):
        if rsp.code != 200:
            if rsp.code == 401:
                raise Unauthorized, "You are not authorized for GSA secure search"
                
            ex = GSAException(rsp.code, rsp.msg)
            try:
                ex.body = rsp.read()
            except:
                pass
            raise ex
        return rsp
            
    def doGet(self,url):
        request = mechanize.Request("%s%s" % (self.encoder(self.url)[0], self.encoder(url)[0]))
        return self.sendRequest(request)
            
    def addCredentials(self, request, cj = None):
        # Add credential cookie
        if cj is None:
            cj = mechanize.CookieJar()
        cookie = self.getCredentialsCookie()
        if cookie:
            cj.set_cookie(cookie)
        cookie = self.getCredentialsCookie('GSACookie2')
        if cookie:
            cj.set_cookie(cookie)
        cj.add_cookie_header(request)
        return request
            
    def sendRequest(self, request):
        data = None
        error = None
        try:
            if self.timeout:
                request.timeout = self.timeout
            cj = mechanize.CookieJar()
            cookie_handler = mechanize.HTTPCookieProcessor(cj)
            request = self.addCredentials(request, cj)
            
            if debug:
                opener = mechanize.build_opener(cookie_handler,
                            mechanize.HTTPHandler(debuglevel=1),
                            mechanize.HTTPSHandler(debuglevel=1))
            else:
                opener = mechanize.build_opener(cookie_handler)
            
            res = opener.open(request)
            res = self.__errcheck(res)
            data = res.read()
            self.saveCookies(cj)
            
            res.fp._sock.recv = None
            res.close()
            del res
            del request
        except urllib2.HTTPError, e:
            logger.warning('The server couldn\'t fulfill the request. Error code: %s' % e.code)
            error = e.code
        except urllib2.URLError, e:
            logger.warning('We failed to reach a server. Reason: %s ' % e.reason)
            error = e.reason
        except GSAException, e:
            logger.warning('The request failed. Reason: %s ' % str(e))
            error = str(e)
            
        return data, error
        
    def search(self, **params):
        request = urllib.urlencode(params, doseq=True)
        if self.only_public:
            access = 'p'
        else:
            access = self.getCredentialsCookie() and 'a' or 'p'
            
        url = u'%s&output=xml_no_dtd&getfields=*&ie=utf8&oe=utf8&filter=0&access=%s' % (safe_unicode(params['q']), access)
        # TODO: better escaping
        url = u'/search?%s' % url.replace(' ','+')
        logger.debug('Searching: %s' % url)
        response, error = self.doGet(url)
        return response, error

    def prepareRequest(self, xml):
        feedtype = u'incremental'
        datasource = safe_unicode(self.source)
        params = []
                
        params.append(("feedtype", feedtype))
        params.append(("datasource", datasource))    
        data=('data','xmlfilename',xml)
        
        content_type, body = encode_multipart_formdata(params, (data,))
        
        headers = self.xmlheaders
        headers['Content-type']=content_type.encode('utf-8')
        #headers['Content-length']=str(len(body.encode('utf-8')))
        
        return body, headers
        
    def doSend(self, body, headers):
        result, error = self.doPost(body, headers)
        # the exception was raised
        if result is None:
            logger.error('Failed to send request')
            return False
        return True
        
    def abort(self):
        pass

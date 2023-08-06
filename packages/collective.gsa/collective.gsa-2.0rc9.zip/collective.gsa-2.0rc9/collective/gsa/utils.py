import re
import time

from zope.component import getUtility
from mechanize import Cookie
from mechanize._headersutil import split_header_words
from mechanize._util import iso2time
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from collective.gsa.interfaces import IGSASchema

rm_html = re.compile('<.+?>')

def isActive():
    """ indicate if the solr connection should/can be used """
    config = getUtility(IRegistry).forInterface(IGSASchema)
    if config is not None:
        return config.active
    return False

security = ClassSecurityInfo()

security.declarePublic('remove_html_tags')
def remove_html_tags(string):
    return rm_html.sub('', string)

def encode_multipart_formdata(fields, files):
    """
    Create data in multipart/form-data encoding
    """
    BOUNDARY = u'----------boundary_of_feed_data$'
    CRLF = u'\r\n'
    L = []
    for (key, value) in fields:
        L.append(u'--' + BOUNDARY)
        L.append(u'Content-Disposition: form-data; name="%s"' % key)
        L.append(u'')
        L.append(value)
    for (key, filename, value) in files:
        L.append(u'--' + BOUNDARY)
        L.append(u'Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append(u'Content-Type: text/xml')
        L.append(u'')
        L.append(value)
    L.append(u'--' + BOUNDARY + u'--')
    L.append(u'')
    body = CRLF.join(L)
    content_type = u'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def safe_unicode(value):
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, 'utf-8')
        except (UnicodeDecodeError):
            value = value.decode('utf-8', 'replace')
    else:
        try:
            value = unicode(value)
        except UnicodeDecodeError:
            pass
            
    return value

def isAnonymous(context):
    membership = getToolByName(context, 'portal_membership')
    return membership.isAnonymousUser()
    
def make_cookie(cookie_str, ignore_discard = False, ignore_expires = False):
    now = time.time()

    boolean_attrs = ("port_spec", "path_spec", "domain_dot",
                     "secure", "discard", "rfc2109")
    value_attrs = ("version",
                   "port", "path", "domain",
                   "expires",
                   "comment", "commenturl")
    
    for data in split_header_words([cookie_str]):
        name, value = data[0]
        standard = {}
        rest = {}
        for k in boolean_attrs:
            standard[k] = False
        for k, v in data[1:]:
            if k is not None:
                lc = k.lower()
            else:
                lc = None
            # don't lose case distinction for unknown fields
            if (lc in value_attrs) or (lc in boolean_attrs):
                k = lc
            if k in boolean_attrs:
                if v is None: v = True
                standard[k] = v
            elif k in value_attrs:
                standard[k] = v
            else:
                rest[k] = v

        h = standard.get
        expires = h("expires")
        discard = h("discard")
        if expires is not None:
            expires = iso2time(expires)
        if expires is None:
            discard = True
        domain = h("domain")
        domain_specified = domain.startswith(".")
        c = Cookie(h("version"), name, value,
                   h("port"), h("port_spec"),
                   domain, domain_specified, h("domain_dot"),
                   h("path"), h("path_spec"),
                   h("secure"),
                   expires,
                   discard,
                   h("comment"),
                   h("commenturl"),
                   rest,
                   h("rfc2109"),
                   ) 
        #if not ignore_discard and c.discard:
        #    return None
        #if not ignore_expires and c.is_expired(now):
        #    return None
        return c

def gsa_installed():
    registry = getUtility(IRegistry)
    try:
        registry.forInterface(IGSASchema)
    except KeyError:
        return False
    return True

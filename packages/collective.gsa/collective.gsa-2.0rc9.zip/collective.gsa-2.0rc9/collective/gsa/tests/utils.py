from os.path import dirname, join
from httplib import HTTPConnection
from threading import Thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from StringIO import StringIO
from socket import error
from sys import stderr
from re import search

from collective.gsa import tests

def getFile(filename, mode='r'):
    """ Return file object """
    filename = join(dirname(tests.__file__), 'data', filename)
    return open(filename, mode)

def getData(filename):
    """Return file as string"""
    filename = join(dirname(tests.__file__), 'data', filename)
    return open(filename, 'r').read()


def fakehttp(solrconn, *fakedata):
    """ helper function to set up a fake http request on a SolrConnection """

    class FakeOutput(list):
        """ helper class to organize output from fake connections """

        conn = solrconn

        def log(self, item):
            self.current.append(item)

        def get(self, skip=0):
            self[:] = self[skip:]
            return ''.join(self.pop(0)).replace('\r', '')

        def new(self):
            self.current = []
            self.append(self.current)

        def __len__(self):
            self.conn.flush()   # send out all pending xml
            return super(FakeOutput, self).__len__()

        def __str__(self):
            self.conn.flush()   # send out all pending xml
            if self:
                return ''.join(self[0]).replace('\r', '')
            else:
                return ''

    output = FakeOutput()

    class FakeSocket(StringIO):
        """ helper class to fake socket communication """

        def sendall(self, str):
            output.log(str)

        def makefile(self, mode, name):
            return self

        def read(self, amt=None):
            if self.closed:
                return ''
            return StringIO.read(self, amt)

        def readline(self, length=None):
            if self.closed:
                return ''
            return StringIO.readline(self, length)

    class FakeHTTPConnection(HTTPConnection):
        """ helper class to fake a http connection object from httplib.py """

        def __init__(self, host, *fakedata):
            HTTPConnection.__init__(self, host)
            self.fakedata = list(fakedata)

        def putrequest(self, *args, **kw):
            response = self.fakedata.pop(0)     # get first response
            self.sock = FakeSocket(response)    # and set up a fake socket
            output.new()                        # and create a new output buffer
            HTTPConnection.putrequest(self, *args, **kw)

        def setTimeout(self, timeout):
            pass

    solrconn.conn = FakeHTTPConnection(solrconn.conn.host, *fakedata)
    return output


def fakemore(solrconn, *fakedata):
    """ helper function to add more fake http requests to a SolrConnection """
    assert hasattr(solrconn.conn, 'fakedata')   # `isinstance()` doesn't work?
    solrconn.conn.fakedata.extend(fakedata)


def fakeServer(actions, port=55555):
    """ helper to set up and activate a fake http server used for testing
        purposes; <actions> must be a list of handler functions, which will
        receive the base handler as their only argument and are used to
        process the incoming requests in turn; returns a thread that should
        be 'joined' when done """
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            action = actions.pop(0)             # get next action
            action(self)                        # and process it...
        def do_GET(self):
            action = actions.pop(0)             # get next action
            action(self)                        # and process it...
        def log_request(*args, **kw):
            pass
    def runner():
        while actions:
            server.handle_request()
    server = HTTPServer(('', port), Handler)
    thread = Thread(target=runner)
    thread.start()
    return thread

def numFound(result):
    match = search(r'numFound="(\d+)"', result)
    if match is not None:
        match = int(match.group(1))
    return match


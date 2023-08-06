from unittest import defaultTestLoader
from collective.gsa.tests.base import GSAFunctionalTestCase, GSATestCase

import base64

# test-specific imports go here...
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility, getUtilitiesFor, getUtility
from collective.gsa.interfaces import IGSASchema
from collective.gsa.interfaces import IGSAConnectionManager
from collective.gsa.interfaces import IGSAQueue
from collective.gsa.interfaces import ISearch

from collective.gsa.tests.utils import getData, getFile, fakehttp, fakeServer
from transaction import commit
from socket import error, timeout
from time import sleep


class UtilityTests(GSATestCase):

    def testGSAQueue(self):
        return
        proc = queryUtility(IGSAQueue)
        # proc is an empty queue - cannot go with failUnless(proc) because bool(proc) is false
        self.failIf(proc is None, 'utility not found')
        self.failUnless(IGSAQueue.providedBy(proc))

    def testSearchInterface(self):
        search = queryUtility(ISearch)
        self.failUnless(search, 'search utility not found')
        self.failUnless(ISearch.providedBy(search))


class IndexTests(GSATestCase):
    
    def afterSetUp(self):
        self.config = getUtility(IRegistry).forInterface(IGSASchema)
        self.config.host = 'localhost'
        self.config.active = False
        self.folder.invokeFactory('Document', id='doc', title='Test document')
        self.folder.invokeFactory('File', id='file', title='Test file')
        self.folder.file.setFile(getFile('file.pdf'))
        
        self.folder.invokeFactory('Folder', id='fold', title='Test folder')
        self.folder.fold.setDescription("test description")
        
    def tearDown(self):
        self.folder.manage_delObjects(['doc', 'file', 'fold'])
    
    def testIndexingDocument(self):
        obj = self.folder.doc
        data = self.indexer.prepareData(self.folder.doc)
        metadata = data['metadata']

        self.assertEqual(data['mimetype'], 'text/html')
        self.assertEqual(metadata['Title'], 'Test document')
        self.failUnless(data['content'].startswith('<![CDATA'))
        

    def testIndexingFile(self):
        obj = self.folder.file

        data = self.indexer.prepareData(obj)
        metadata = data['metadata']
        self.assertEqual(data['mimetype'], 'application/pdf')
        self.assertEqual(metadata['Title'], 'Test file')
        self.assertEqual(data['content_encoding'], 'base64binary')
        self.failUnless(base64.decodestring(data['content']).startswith('%PDF-1.3'))

    def testIndexingFolder(self):
        obj = self.folder.fold

        data = self.indexer.prepareData(obj)
        metadata = data['metadata']
        self.assertEqual(data['mimetype'], 'text/plain')
        self.assertEqual(metadata['Title'], 'Test folder')
        self.assertEqual(data['content'], u'Test folder - test description')
        
    def testXMLDocument(self):
        # first commit so we now what is in the queue
        commit()
        self.config.active=True
        
        obj = self.folder.doc
        queue = getUtility(IGSAQueue)

        self.failUnless(len(queue) == 0)
        self.indexer.index(obj)
        self.failUnless(len(queue) == 1)
        
        conn = self.indexer.getConnection()
        xml, prcs = conn.prepareXML(False)
        body, headers = conn.prepareRequest(xml)
        self.failUnless(body.startswith(getData('request.txt')))
        self.config.active=False
        
def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)


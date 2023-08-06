__author__ = 'chimezieogbuji'

import unittest, amara, os, urllib2
from cStringIO import StringIO

from shutil import rmtree

from server_support import server

from rdflib.Graph import Graph, ConjunctiveGraph
from rdflib import URIRef, plugin, RDF, RDFS, BNode, Namespace, Literal
from rdflib.util import first

from akamu.diglot import Manager, Resource
from akamu.config.dataset import DestroyOrCreateDataset
from akamu.xslt import TransformWithAkamuExtensions
from amara import bindery

from IsomorphicTestableGraph import IsomorphicTestableGraph

from amara.namespaces import *
from amara import tree
from amara.writers.struct import structwriter, E, NS, ROOT
from amara.lib import U

VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
FOAF  = Namespace('http://xmlns.com/foaf/0.1/')

TEST_ROOT_DIR_PATH  = '/tmp/diglotDir'
TEST_DIR_PATH       = '/tmp/diglotDir/patients'
TEST_XSLT_PATH      = '/tmp/diglotDir/xslt'

def TestGraphUriFn(path,fName):
    return 'http://example.com%s'%path.split('.')[0]

class TestDiglotCapabilities(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEST_DIR_PATH)
        os.makedirs(TEST_XSLT_PATH)
        f=open(os.path.join(TEST_XSLT_PATH,'grddl.xslt'),'w')
        f.write(open('test/foaf.xslt').read())
        f.close()

        self.store = Graph().store
        self.mgr = Manager(TEST_ROOT_DIR_PATH,
                           self.store,
                           graphUriFn=TestGraphUriFn,
                           transforms4Dir={
                               u'/patients' : u'/xslt/grddl.xslt'
                           })
        src    = StringIO()
        w = structwriter(indent=u"yes", stream=src)
        w.feed(
            ROOT(
                E(u'Patient',{ u'name' : u'Chimezie Ogbuji', u'gender' : u'Male'})
            )
        )
        self.ptDoc = src.getvalue()
        self.ptUri   = URIRef('http://example.com/patients/ptRec01')
        self.server = server()

    def test_create_and_mirrored(self):

        path = '/patients/ptRec01.xml'

        self.mgr.createResource(path,self.ptDoc)

        ptGraph = Graph(self.store,identifier=self.ptUri)

        msg = "No faithful rendition of %s in %s!"%(
            '/patients/ptRec01.xml',
            self.ptUri
        )
        self._test_via_sparql(ptGraph, msg, "Chimezie Ogbuji")

    def test_create_and_update(self):

        path = '/patients/ptRec01.xml'

        res = self.mgr.createResource(path,self.ptDoc)

        ptGraph = Graph(self.store,identifier=self.ptUri)

        msg = "No faithful rendition of %s in %s!"%(
            '/patients/ptRec01.xml',
            self.ptUri
        )
        self._test_via_sparql(ptGraph, msg, "Chimezie Ogbuji")

        src    = StringIO()
        w = structwriter(indent=u"yes", stream=src)
        w.feed(
            ROOT(
                E(u'Patient',{ u'name' : u'Uche Ogbuji', u'gender' : u'Male'})
            )
        )
        res.update(src.getvalue())

        ptGraph = Graph(self.store,identifier=self.ptUri)
        self._test_via_sparql(ptGraph, "Name wasn't updated", "Uche Ogbuji")

        rt = list(ptGraph.query(
            'SELECT ?NAME { [] a foaf:Person; foaf:businessCard [ v:fn ?NAME ] } ',
            initNs={
                u'foaf' : FOAF,
                u'v'    : VCARD }
        ))
        self.failUnless(len(rt)==1,"More than one name in graph (should only be Uche)")
        self.failUnless(first(rt) == Literal('Uche Ogbuji'),"Old name still in faithful rendition")

    def test_get_resource(self):

        path = '/patients/ptRec01.xml'

        self.mgr.createResource(path,self.ptDoc)

        doc = amara.parse(self.mgr.getResource(path).getContent())

        self.failUnless(doc.xml_select('/Patient') and
                        doc.xml_select('/Patient[@name = "Chimezie Ogbuji"]'))
        self.failUnless(doc.xml_select('/Patient'))

    def test_delete_resource(self):
        path = '/patients/ptRec01.xml'

        self.mgr.createResource(path,self.ptDoc)

        self.mgr.deleteResource('/patients/ptRec01.xml')
        ptGraph = Graph(self.store,identifier=self.ptUri)

        self.failUnless(not len(ptGraph),"Faithful rendition should be erased with removal of resource")

    def _test_via_sparql(self, graph, msg, name):
        query = 'ASK { [] a foaf:Person; foaf:businessCard [ v:fn "%s" ] } '%(
            name
        )
        queryAns = graph.query(
            query,
            initNs={
                u'foaf': FOAF,
                u'v'   : VCARD}
        )
        self.failUnless(queryAns.askAnswer[0], msg)

    def test_grddl_graph_store(self):
        from GRDDLAmara import WebMemo, GRDDLAgent

        path = '/patients/ptRec01.xml'

        req = urllib2.Request(
            self.server[:-1]+'/diglot'+path,
            headers={ "Content-Type" : "application/xml" }
        )
        req.get_method = lambda: 'PUT'
        urllib2.urlopen(req,data=self.ptDoc)

#        self.mgr.createResource(path,self.ptDoc)

#        ptGraph = Graph(self.store,identifier=self.ptUri)
#
#        msg = "No faithful rendition of %s in %s!"%(
#            '/patients/ptRec01.xml',
#            self.ptUri
#        )
#        self._test_via_sparql(ptGraph, msg, "Chimezie Ogbuji")

        fullPath = "diglot%s"%path

        grddlResult = IsomorphicTestableGraph()
        GRDDLAgent(
            self.server + fullPath,
            grddlResult,
            WebMemo(),
            useXInclude=True,
            DEBUG = True
        )

        msg = "GET to %s didn't return GRDDL source document"%(
            self.server + fullPath
        )
        self._test_via_sparql(grddlResult, msg, "Chimezie Ogbuji")

        personUri = first(grddlResult.subjects(RDF.type,FOAF.Person))

        #POSTing XML to transform returns the GRDDL result
        req = urllib2.Request(
            self.server + "diglot/xslt/grddl.xslt",
            headers={ "Content-Type" : "application/xml" }
        )
        response = urllib2.urlopen(req,data=self.ptDoc)
        rt=response.read()
        responseGraph = IsomorphicTestableGraph().parse(StringIO(rt),publicID=personUri)

        self.failUnless(grddlResult == responseGraph,
            "Incorrect GRDDL result returned by POST to transform"
        )

        #POSTing RDF to transform returns the corresponding XML source
        #(using reverse transform)
        req = urllib2.Request(
            self.server + "diglot/xslt/grddl.xslt?base=%s"%urllib2.quote(personUri),
            headers={ "Content-Type" : "application/rdf+xml" }
        )
        response = urllib2.urlopen(req,data=grddlResult.serialize(format='pretty-xml'))
        doc = bindery.parse(response.read())
        self.failUnless(
            doc.xml_select('/Patient[@name = "Chimezie Ogbuji"]'),
            "Document doesn't match GRDDL source: %s"%rt
        )

        #POSTing XML to directory will add it to the directory using a generated
        #file name, which is returned in Location header
        src    = StringIO()
        w = structwriter(indent=u"yes", stream=src)
        w.feed(
            ROOT(
                E(u'Patient',{ u'name' : u'Uche Ogbuji'})
            )
        )
        xmlSrc = src.getvalue()
        req = urllib2.Request(
            self.server + "diglot/patients",
            headers={ "Content-Type" : "application/xml" }
        )
        response = urllib2.urlopen(req,data=xmlSrc)
        self.failUnless('Location' in response.info(),"No Location header returned")
        self.failUnless(response.getcode() == 201,"Didn't respond with 201 Created")
        location = response.info()['Location']

        grddlResult = Graph()
        GRDDLAgent(
            self.server[:-1]+location,
            grddlResult,
            WebMemo(),
            useXInclude=True,
            DEBUG = True
        )

        msg = "GET to %s didn't return GRDDL source document" % location
        self._test_via_sparql(grddlResult, msg, "Uche Ogbuji")

        #POSTing RDF to directory is same as GSP (using reverse mapping)
        req = urllib2.Request(
            self.server + "diglot/patients",
            headers={ "Content-Type" : "application/rdf+xml" }
        )
        response = urllib2.urlopen(req,data=grddlResult.serialize(format='pretty-xml'))
        self.failUnless('Location' in response.info(),"No Location header returned")
        self.failUnless(response.getcode() == 201,"Didn't respond with 201 Created")
        location = response.info()['Location']

        grddlResult = Graph()
        GRDDLAgent(
            self.server[:-1]+location,
            grddlResult,
            WebMemo(),
            useXInclude=True,
            DEBUG = True
        )

        msg = "GET to %s didn't return GRDDL source document" % location
        self._test_via_sparql(grddlResult, msg, "Uche Ogbuji")

        #XUpdate to change name
        xupdate = """<?xml version="1.0"?>
<xupdate:modifications
  version="1.0"
  xmlns:xupdate="http://www.xmldb.org/xupdate">
  <xupdate:update select="/Patient/@name">Chimezie Ogbuji</xupdate:update>
</xupdate:modifications>"""
        req = urllib2.Request(
            self.server[:-1]+location,
            headers={ "Content-Type" : "application/xml" }
        )
        req.get_method = lambda: 'PATCH'
        urllib2.urlopen(req,data=xupdate)

        req = urllib2.Request(self.server[:-1]+location)
        doc = bindery.parse(urllib2.urlopen(req).read())
        self.failUnless(
            doc.xml_select('/Patient[@name = "Chimezie Ogbuji"]'),
            "Document doesn't match GRDDL source: %s"%rt
        )


        #XSLT to change name
        xsltSrc = """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
        xmlns:xsl   = "http://www.w3.org/1999/XSL/Transform"
        version     = "1.0">
    <xsl:template match="/">
        <xsl:apply-templates  />
    </xsl:template>
    <xsl:template match="@name">
        <xsl:attribute name="name" >Uche Ogbuji</xsl:attribute>
    </xsl:template>
    <xsl:template match="@*|node()">
        <xsl:copy>
          <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet> """
        req = urllib2.Request(
            self.server[:-1]+location,
            headers={ "Content-Type" : "application/xslt+xml" }
        )
        req.get_method = lambda: 'PATCH'
        urllib2.urlopen(req,data=xsltSrc)

        req = urllib2.Request(self.server[:-1]+location)
        doc = bindery.parse(urllib2.urlopen(req).read())
        self.failUnless(
            doc.xml_select('/Patient[@name = "Uche Ogbuji"]'),
            "Document doesn't match GRDDL source: %s"%rt
        )


        req = urllib2.Request(self.server[:-1]+location)
        req.get_method = lambda: 'DELETE'
        resp = urllib2.urlopen(req)
        self.failUnless(resp.getcode() == 204,"Wrong response code: %s"%resp.getcode())

        notFound = False
        try:
            urllib2.urlopen(self.server[:-1]+location)
        except urllib2.URLError, e:
            if e.code == 404: notFound = True

        self.failUnless(notFound,"%s should have been removed by DELETE"%(self.server[:-1]+location))

        src    = StringIO()
        w = structwriter(indent=u"yes", stream=src)
        w.feed(
            ROOT(
                E(u'Patient',{ u'name' : u'Ejike Ogbuji'})
            )
        )
        xmlSrc = src.getvalue()

        req = urllib2.Request(
            self.server[:-1]+'/diglot'+path,
            headers={ "Content-Type" : "application/xml" }
        )
        req.get_method = lambda: 'PUT'
        urllib2.urlopen(req,data=xmlSrc)

        grddlResult = Graph()
        GRDDLAgent(
            self.server[:-1]+'/diglot'+path,
            grddlResult,
            WebMemo(),
            useXInclude=True,
            DEBUG = True
        )
        msg = "GET to resource created by PUT (/patients/ptRec01.xml) didn't return GRDDL source document"
        self._test_via_sparql(grddlResult, msg, "Ejike Ogbuji")

    def tearDown(self):
        rmtree(TEST_ROOT_DIR_PATH)

class TestAkamuExtensions(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEST_DIR_PATH)
        os.makedirs(TEST_XSLT_PATH)
        f=open(os.path.join(TEST_XSLT_PATH,'grddl.xslt'),'w')
        f.write(open('test/foaf.xslt').read())
        f.close()

        self.server = server()

    def test_diglot_extensions_basic(self):
        req = urllib2.Request(self.server + "diglot_extensions_basic_test?rootPath=%s"%TEST_ROOT_DIR_PATH)
        response = urllib2.urlopen(req).read()
        self.failUnless(response == 'Success')

    def tearDown(self):
        rmtree(TEST_ROOT_DIR_PATH)

if __name__ == '__main__':
#    suite = unittest.TestLoader().loadTestsFromTestCase(TestAkamuExtensions)
#    unittest.TextTestRunner(verbosity=3).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDiglotCapabilities)
    unittest.TextTestRunner(verbosity=3).run(suite)
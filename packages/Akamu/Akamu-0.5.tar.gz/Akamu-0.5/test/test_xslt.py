__author__ = 'chimezieogbuji'

import unittest, urllib, urllib2
from cStringIO import StringIO
from server_support import server
from rdflib.Graph import Graph
from rdflib import Namespace
from akamu.config.dataset import DestroyOrCreateDataset
from akamu.xslt import TransformWithAkamuExtensions

VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
FOAF  = Namespace('http://xmlns.com/foaf/0.1/')

NS_MAPPING = {
    u'foaf' : FOAF,
    u'v'    : VCARD
}

class TestRestTransform(unittest.TestCase):
    def setUp(self):
        self.server = server()

    def test_invoke_get(self):
        req = urllib2.Request(self.server + "xslt_rest_get?name=Uche+Ogbuji")
        response = urllib2.urlopen(req)
        g = Graph().parse(response)

        queryAns = g.query(
            'ASK { [] a foaf:Person; foaf:businessCard [ v:fn "Uche Ogbuji" ] } ',
            initNs=NS_MAPPING
        )
        self.failUnless(queryAns.askAnswer[0])

        req = urllib2.Request(self.server + "xslt_rest_get?name=Uche+Ogbuji")
        response = urllib2.urlopen(req)
        g = Graph().parse(response)

        queryAns = g.query(
            'ASK { [] a foaf:Person; foaf:businessCard [ v:fn "Chimezie Ogbuji" ] } ',
            initNs=NS_MAPPING
        )
        self.failUnless(queryAns.askAnswer[0])

    def test_invoke_post(self):
        from httplib2 import Http
        h = Http()
        resp, content = h.request(
                self.server + "xslt_rest_post",
                "POST",
                urllib.urlencode({'name': 'Uche Ogbuji'})
        )
        g = Graph().parse(StringIO(content))

        queryAns = g.query(
            'ASK { [] a foaf:Person; foaf:businessCard [ v:fn "Uche Ogbuji" ] } ',
            initNs=NS_MAPPING
        )
        self.failUnless(queryAns.askAnswer[0])

        h = Http()
        resp, content = h.request(
            self.server + "xslt_rest_post",
            "POST",
            urllib.urlencode({})
        )

        g = Graph().parse(StringIO(content))

        queryAns = g.query(
            'ASK { [] a foaf:Person; foaf:businessCard [ v:fn "Chimezie Ogbuji" ] } ',
            initNs=NS_MAPPING
        )
        self.failUnless(queryAns.askAnswer[0])

class TestAkamuExtensions(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEST_DIR_PATH)
        os.makedirs(TEST_XSLT_PATH)
        f=open(os.path.join(TEST_XSLT_PATH,'grddl.xslt'),'w')
        f.write(open('test/foaf.xslt').read())
        f.close()

        self.server = server()

    def test_diglot_extensions_basic(self):
        TransformWithAkamuExtensions(src,xform,baseUri,params,manager)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRestTransform)
    unittest.TextTestRunner(verbosity=5).run(suite)
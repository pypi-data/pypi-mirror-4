import unittest, os, urllib, urllib2, re, httplib2, shutil, base64
from rdflib.store import Store, NO_STORE
from rdflib.Graph import Graph, ConjunctiveGraph
from rdflib import plugin, BNode, Namespace, Literal, OWL
from server_support import server
from akamu.diglot import Manager, Resource

TEST_ROOT_DIR_PATH  = '/tmp/diglotDir'
TEST_DIR_PATH       = '/tmp/diglotDir/acl'
TEST_XSLT_PATH      = '/tmp/diglotDir/xslt'

def TestGraphUriFn(path,fName):
    return 'http://example.com%s'%path.split('.')[0]

class TestWebACLCapabilities(unittest.TestCase):
    def setUp(self):
        mysqluser,mysqlpw,mysqlhost,mysqldb = os.environ.get(
            "MYSQL_CREDENTIALS",
            ",,,"
        ).split(',')
        configStr = 'user=%s,password=%s,db=%s,host=localhost'%(
            mysqluser,
            mysqlpw,
            mysqldb
        )
        store = plugin.get('MySQL', Store)('test')
        rt = store.open(configStr,create=False)
        if rt == NO_STORE:
            store.open(configStr,create=True)
        else:
            store.destroy(configStr)
            store.open(configStr,create=True)
        store.open(configStr,create=False)

        os.makedirs(TEST_DIR_PATH)
        os.makedirs(TEST_XSLT_PATH)
        f=open(os.path.join(TEST_XSLT_PATH,'acl_grddl.xslt'),'w')
        f.write(open('test/acl_grddl.xslt').read())
        f.close()

        self.store = store
        self.mgr = Manager(TEST_ROOT_DIR_PATH,
                           self.store,
                           graphUriFn=TestGraphUriFn,
                           transforms4Dir={
                               u'/acl' : u'/xslt/acl_grddl.xslt'
                           })
        path = '/acl/1.xml'
        self.mgr.createResource(path,open('test/test_user.xml').read())
        self.server = server()

    def tearDown(self):
        shutil.rmtree(TEST_DIR_PATH)
        shutil.rmtree(TEST_XSLT_PATH)

    def test_basic_unauthorized(self):
        url_pattern = re.compile("http://localhost:[0-9]+/login\?came_from")
        req = urllib2.Request(self.server + "service.1")

        handler = SmartRedirectHandler()
        opener = urllib2.build_opener(handler)
        self.failUnlessRaises(urllib2.HTTPError,opener.open,req)
        self.failUnless('Location' in handler.headers,"No Location header returned")
        self.failUnless(url_pattern.match(handler.headers['Location']),
                        "Didn't redirect to /login")

    def test_any_authorized(self):
        h = httplib2.Http()
        h.add_credentials('admin', 'admin',"repoze.who")
        resp, content = h.request(
            self.server + "service.2",
            headers = { "Authorization" :
                            "Basic {0}".format(
                                base64.b64encode("{0}:{1}".format('admin', 'admin')))})
        self.failUnlessEqual(resp.status,200)
        self.failUnlessEqual(content,"Success")

    def test_group_authorized(self):
        h = httplib2.Http()
        h.add_credentials('admin', 'admin',"repoze.who")
        resp, content = h.request(
            self.server + "service.1",
            headers = { "Authorization" :
                            "Basic {0}".format(
                                base64.b64encode("{0}:{1}".format('admin', 'admin')))})
        self.failUnlessEqual(resp.status,200)
        self.failUnlessEqual(content,"Success")

        h = httplib2.Http()
        h.add_credentials('admin', 'admin',"repoze.who")
        resp, content = h.request(
            self.server + "service.3",
            headers = { "Authorization" :
                            "Basic {0}".format(
                                base64.b64encode("{0}:{1}".format('admin', 'admin')))})
        self.failUnlessEqual(resp.status,403)

    def test_no_write(self):
        h = httplib2.Http()
        h.add_credentials('admin', 'admin',"repoze.who")
        resp, content = h.request(
            self.server + "service.1","POST", body="This is text",
            headers = { "Authorization" :
                            "Basic {0}".format(
                                base64.b64encode("{0}:{1}".format('admin', 'admin'))) ,
                        'content-type':'text/plain'}
        )
        self.failUnlessEqual(resp.status,403)

    def test_append_no_write(self):
        h = httplib2.Http()
        h.add_credentials('admin', 'admin',"repoze.who")
        resp, content = h.request(
            self.server + "service.2","PUT", body="This is text",
            headers = { "Authorization" :
                            "Basic {0}".format(
                                base64.b64encode("{0}:{1}".format('admin', 'admin'))),
                        'content-type':'text/plain'}
        )
        self.failUnlessEqual(resp.status,403)

        h = httplib2.Http()
        h.add_credentials('admin', 'admin',"repoze.who")
        resp, content = h.request(
            self.server + "service.2","POST", body="This is text",
            headers = { "Authorization" :
                            "Basic {0}".format(
                                base64.b64encode("{0}:{1}".format('admin', 'admin'))),
                        'content-type':'text/plain'}
        )
        self.failUnlessEqual(resp.status,200)
        self.failUnlessEqual(content,"Success")

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, headers)
        result.status = code
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        self.headers = headers
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        result.status = code
        return result

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWebACLCapabilities)
    unittest.TextTestRunner(verbosity=3).run(suite)
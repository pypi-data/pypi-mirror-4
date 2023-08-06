__author__ = 'chimezieogbuji'

import unittest, urllib, urllib2, amara
import httplib2
from cStringIO import StringIO
from server_support import server
from rdflib.Graph import Graph
from rdflib import Namespace

VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
FOAF  = Namespace('http://xmlns.com/foaf/0.1/')

NS_MAPPING = {
    u'foaf' : FOAF,
    u'v'    : VCARD
}

class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(
            req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result

class NotModifiedHandler(urllib2.BaseHandler):

    def http_error_304(self, req, fp, code, message, headers):
        addinfourl = urllib2.addinfourl(fp, headers, req.get_full_url())
        addinfourl.code = code
        return addinfourl

class TestWheezyWrapper(unittest.TestCase):
    def setUp(self):
        self.server = server()

    def test_invoke_get(self):
        addr = self.server + "wheezy.test"
#        print addr
#        h = httplib2.Http(".cache")
#        md, content = h.request(addr)
#        md, content = h.request(addr,headers={'cache-control':'no-cache'})
#        print md['etag'], md.status, md
#        etag = md['etag']
#        code = md.status

        response = urllib2.urlopen(addr)
        code = response.getcode()
        self.failUnless(code == 200)
        headers = response.info()
        etag = headers.getheader("ETag")
        self.failUnless(etag == '12345')
        doc = amara.parse(response)
        self.failUnless(
            doc.xml_select(
                '/xhtml:html/xhtml:body/xhtml:p',
                prefixes={
                    u'xhtml':u'http://www.w3.org/1999/xhtml' }
            )
        )

        request = urllib2.Request(addr)
        opener = urllib2.build_opener(DefaultErrorHandler())
        request.add_header('If-None-Match',etag)
#        print request.headers
        seconddatastream = opener.open(request)
        code = seconddatastream.getcode()
#        print seconddatastream.headers
        self.failUnless(code == 304,"%s is not 304"%code)

#        response = urllib2.urlopen(self.server + "wheezy.test.clear_cache")
#        code = response.getcode()
#        self.failUnless(code == 200)
#
#        request = urllib2.Request(addr)
#        opener = urllib2.build_opener(DefaultErrorHandler())
#        request.add_header('If-None-Match',etag)
#        print request.headers
#        seconddatastream = opener.open(request)
#        code = seconddatastream.getcode()
#        print seconddatastream.headers
#        self.failUnless(code == 200,"%s is not 200"%code)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWheezyWrapper)
    unittest.TextTestRunner(verbosity=5).run(suite)
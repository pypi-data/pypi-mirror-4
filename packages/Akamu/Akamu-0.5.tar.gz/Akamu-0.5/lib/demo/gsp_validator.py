# -*- coding: utf-8 -*-
import httplib2, os,cgi
from akara                          import request, logger, module_config as config
from rdflib                         import URIRef
from rdflib.Graph                   import Graph
from rdflib_tools.GraphIsomorphism  import IsomorphicTestableGraph
from amara.lib                      import iri
from amara.lib.util                 import *
from amara.writers.struct           import structwriter, E, NS, ROOT, RAW
from akara.services                 import simple_service, service
from akamu.xslt                     import xslt_rest, NOOPXML
from akamu.config.dataset           import GetParameterizedQuery
from cStringIO                      import StringIO
from urlparse                       import urlparse

XHTML_IMT  = 'application/xhtml+xml'
HTML_IMT   = 'text/html'
XML_IMT    = 'application/xml'
SERVICE_ID = 'http://code.google.com/p/akamu/wiki/GraphStoreProtocol'
TEST_NS    = 'http://www.w3.org/2009/sparql/docs/tests/data-sparql11/http-rdf-update/tests.html'

@simple_service('GET', SERVICE_ID, 'gsp.validator.form',HTML_IMT+';charset=utf-8')
@xslt_rest(
    os.path.join(
        config().get('demo_path'),
        'gsp_validator.xslt'),
    source=NOOPXML)
def validator_form(): pass

def post_multipart(host, selector, files):
    """
    from http://code.activestate.com/recipes/146306/

    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    import httplib
    content_type, body = encode_multipart_formdata(files)
    h = httplib.HTTPSConnection(host)
    header = {
        'Content-Type'  : content_type,
        'Content-Length': len(body)
    }
    h.request('POST', selector, body, header)
    res = h.getresponse()
    return res.status, res.reason, res.read()

def encode_multipart_formdata(files):
    """
    from http://code.activestate.com/recipes/146306/

    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY1 = 'ThIs_Is_tHe_outer_bouNdaRY_$'
    BOUNDARY2 = 'ThIs_Is_tHe_inner_bouNdaRY_$'
    CRLF = '\r\n'
    L = []

    L.append('--' + BOUNDARY1)
    L.append('Content-Disposition: form-data; name="graphs"')
    L.append('Content-Type: multipart/mixed; boundary=%s'%BOUNDARY2)
    L.append('')

    for (filename, mtype, value) in files:
        L.append('--' + BOUNDARY2)
        L.append('Content-Disposition: file; filename="%s"' % (filename,))
        L.append('Content-Type: %s' % mtype)
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY2)
    L.append('--' + BOUNDARY1)
#    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY1
    return content_type, body

TESTS = [
    "PUT - Initial state",
    "GET of PUT - Initial state",
    "PUT - graph already in store",
    "GET of PUT - graph already in store",
    "PUT - default graph",
    "GET of PUT - default graph",
    "PUT - mismatched payload",
    "PUT - empty graph",
    "GET of PUT - empty graph",
    "DELETE - existing graph",
    "GET of DELETE - existing graph",
    "DELETE - non-existent graph",
    "POST - existing graph",
    "GET of POST - existing graph",
    "POST - multipart/form-data",
    "GET of POST - multipart/form-data",
    "POST - create  new graph",
    "GET of POST - create  new graph",
    "POST - empty graph to existing graph",
    "GET of POST - after noop",
    "HEAD on an existing graph",
    "HEAD on a non-existing graph",
]

GRAPH1=\
u"""<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf ="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:v   ="http://www.w3.org/2006/vcard/ns#"
    >
    <foaf:Person rdf:about="%s">
        <foaf:businessCard>
            <v:VCard>
                <v:fn>%s</v:fn>
            </v:VCard>
        </foaf:businessCard>
    </foaf:Person>
</rdf:RDF>"""

GRAPH2=\
u"""<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf ="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:v   ="http://www.w3.org/2006/vcard/ns#"
    >
    <foaf:Person rdf:about="%s">
        <foaf:businessCard>
            <v:VCard>
                <v:given-name>%s</v:given-name>
            </v:VCard>
        </foaf:businessCard>
    </foaf:Person>
</rdf:RDF>"""

GRAPH3=\
u"""<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf ="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:v   ="http://www.w3.org/2006/vcard/ns#"
    >
    <rdf:Description rdf:about="%s">
        <foaf:name>%s</foaf:name>
    </rdf:Description>
</rdf:RDF>"""

GRAPH4=\
u"""<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf ="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:v   ="http://www.w3.org/2006/vcard/ns#"
    >
    <foaf:Person rdf:about="%s">
        <foaf:name>%s</foaf:name>
        <foaf:businessCard>
            <v:VCard>
                <v:fn>%s</v:fn>
            </v:VCard>
        </foaf:businessCard>
    </foaf:Person>
</rdf:RDF>"""

GRAPH5=\
u"""<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf ="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:v   ="http://www.w3.org/2006/vcard/ns#"
    >
    <rdf:Description rdf:about="%s">
        <foaf:familyName>%s</foaf:familyName>
    </rdf:Description>
</rdf:RDF>
"""

GRAPH6=\
u"""<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf ="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:v   ="http://www.w3.org/2006/vcard/ns#"
    >
    <rdf:Description rdf:about="%s">
        <foaf:givenName>%s</foaf:givenName>
    </rdf:Description>
</rdf:RDF>
"""

graphs = {
    "PUT - Initial state"                   : (GRAPH1,"person/1",'xml',"John Doe"),
    "PUT - graph already in store"          : (GRAPH1,"person/1",'xml',"Jane Doe"),
    "PUT - default graph"                   : (GRAPH2,"",'xml',"Alice"),
    "PUT - mismatched payload"              : (GRAPH1,"person/1",'xml',"Jane Doe"),
    "PUT - empty graph"                     : (None,None,None,None),
    "PUT - replace empty graph"             : (GRAPH2,"",'xml',"Alice"),
    "POST - existing graph"                 : (GRAPH3,"person/1","xml","Jane Doe"),
    "GET of POST - existing graph"          : (GRAPH4,"person/1","xml",("Jane Doe",)*2),
    "POST - create  new graph"              : (GRAPH2,"",'xml',"Alice"),
    "POST - empty graph to existing graph"  : (None,None,None,None),
    "multipart/form-data graph 1"           : (GRAPH5,"person/1",'xml',"Doe"),
    "multipart/form-data graph 2"           : (GRAPH6,"person/1",'xml',"Jane"),
}

class GraphStoreValidator(object):
    def __init__(self,graph_store_url):
        self.graph_store_url = graph_store_url
        self.graphs = graphs
        self.graph_store_url_base = graph_store_url \
            if graph_store_url[-1] == '/' else graph_store_url + '/'

        for testName,(src,relUrl,format,name) in list(self.graphs.items()):
            if src is None:
                self.graphs[testName] = None
            else:
                graphIri = URIRef(iri.absolutize(relUrl,self.graph_store_url_base))
                if isinstance(name,tuple):
                    params = (graphIri,)+name
                    src = src%params
                else:
                    src = src%(graphIri,name)
                self.graphs[testName] = IsomorphicTestableGraph().parse(StringIO(src),
                                                               format=format)

    def yieldResultElem(self,testName,successful,url,message=None):
        path_and_query = urlparse(url).path
        path_and_query = path_and_query + u'?' + urlparse(url
            ).query if urlparse(url).query else path_and_query
        attrs = {
            u'path'   : path_and_query,
            u'name'   : testName,
            u'result' : u'passed' if successful else u'failed'
        }

        if testName in TESTS:
            testId = testName.replace(' ','_').replace('-','').lower()
            attrs['id'] = testId

        if message:
            return E(
                (TEST_NS,u'Result'),attrs,message
            )
        else:
            return E(
                (TEST_NS,u'Result'),attrs
            )

    def graphSubmit(
            self,
            h,
            url,
            testName,
            getTestName=None,
            expectedStatus=201,
            imt='text/turtle',
            format='n3',
            method='PUT',
            responseInfo=None):
        responseInfo = responseInfo if responseInfo is not None else []
        graph = self.graphs[testName]
        body = graph.serialize(format=format) if graph is not None else u""
        resp, content = h.request(url,
            method,
            body=body,
            headers={
                'content-type'   : imt,
                'cache-control'  : 'no-cache',
                'content-length' : str(len(body))
            } )
        responseInfo.append((resp,content))
        if resp.status != expectedStatus:
            yield self.yieldResultElem(
                testName,
                False,
                url,
                u'expected status %s, received %s (%s)'%(
                    expectedStatus,
                    resp.status,
                    content
                )
            )
        else:
            yield self.yieldResultElem(testName,True,url)
        if getTestName:
            for el in self.isomorphCheck(testName,h,url,getTestName):
                yield el

    def isomorphCheck(self,testName,h,url,alternativeTestName=None):
        resp, content = h.request(url,"GET",headers={
            'content-type' : 'text/turtle',
            'cache-control': 'no-cache',
            'Accept'       : 'text/turtle; charset=utf-8'
        })
        getTestName = alternativeTestName if alternativeTestName else testName
        if resp.status == 200:
            if 'content-type' not in resp or resp['content-type'].find('text/turtle')+1:
                g1=IsomorphicTestableGraph().parse(
                    StringIO(content),
                    format='n3') if content is not None else None
                if g1 != self.graphs[testName]:
                    yield self.yieldResultElem(
                        getTestName,
                        False,
                        url,
                        u'unexpected returned RDF graph'
                    )
                else:
                    yield self.yieldResultElem(getTestName,True,url)
            elif 'content-type' in resp:
                yield self.yieldResultElem(
                    getTestName,
                    False,
                    url,
                    u'expected returned content-type of text/turtle, received %s'%(
                        resp['content-type']
                        )
                )
        else:
            yield self.yieldResultElem(
                getTestName,
                False,
                url,
                u'expected status %s, received %s (%s)'%(
                    200,resp.status,content
                    )
            )

    def runTests(self):
        h = httplib2.Http()
        url      = iri.absolutize("person/1.ttl",self.graph_store_url_base)

        for el in self.graphSubmit(h,url,"PUT - Initial state","GET of PUT - Initial state"):
            yield el

        testName = u"PUT - graph already in store"
        for el in self.graphSubmit(
                            h,
                            url,
                            testName,
                            expectedStatus=204,
                            getTestName="GET of PUT - graph already in store"):
            yield el

        url = self.graph_store_url_base+'?default'
        testName = "PUT - default graph"
        for el in self.graphSubmit(h,url,testName,"GET of PUT - default graph"):
            yield el

        h = httplib2.Http()
        url      = iri.absolutize("person/1.ttl",self.graph_store_url_base)
        testName = "PUT - mismatched payload"
        for el in self.graphSubmit(h,url,testName,expectedStatus=400,imt='application/rdf+xml'):
            yield el

        h = httplib2.Http()
        url      = iri.absolutize("person/2.ttl",self.graph_store_url_base)
        for el in self.graphSubmit(h,url,"PUT - empty graph","GET of PUT - empty graph"):
            yield el

        h = httplib2.Http()
        url      = iri.absolutize("person/2.ttl",self.graph_store_url_base)
        for el in self.graphSubmit(h,url,"PUT - replace empty graph","GET of replacement for empty graph"):
            yield el

        testName = "DELETE - existing graph"
        resp, content = h.request(url,"DELETE")
        if resp.status != 200:
            yield self.yieldResultElem(
                testName,
                False,
                url,
                u'expected status %s, received %s (%s)'%(
                    200,
                    resp.status,
                    content
                    )
            )
        else:
            yield self.yieldResultElem(testName,True,url)

        testName = "GET of DELETE - existing graph"
        resp, content = h.request(url,"GET",headers={
            'cache-control': 'no-cache',
        })

        if resp.status == 404:
            yield self.yieldResultElem(testName,True,url)
        else:
            yield self.yieldResultElem(
                testName,
                False,
                url,
                u'expected status %s, received %s (%s)'%(
                    404,
                    resp.status,
                    content
                    )
            )

        testName = "DELETE - non-existent graph"
        resp, content = h.request(url,"DELETE")
        if resp.status == 404:
            yield self.yieldResultElem(testName,True,url)
        else:
            yield self.yieldResultElem(
                testName,
                False,
                url,
                u'expected status %s, received %s (%s)'%(
                    404,
                    resp.status,
                    content
                    )
            )

        h = httplib2.Http()
        url      = iri.absolutize("person/1.ttl",self.graph_store_url_base)
        testName = "POST - existing graph"
        for el in self.graphSubmit(h,url,testName,expectedStatus=200,method='POST'):
            yield el
        for el in self.isomorphCheck(
            "GET of POST - existing graph",
            h,
            url,
            alternativeTestName="GET of POST - existing graph"):
            yield el

        h = httplib2.Http()
        url      = self.graph_store_url_base
        testName = "POST - create  new graph"
        responseInfo = []
        for el in self.graphSubmit(
            h,
            url,
            testName,
            expectedStatus=201,
            method='POST',
            responseInfo=responseInfo):
            yield el
        if responseInfo:
            resp,content = responseInfo[0]
            if 'location' in resp:
                yield self.yieldResultElem(testName+" (returns new location)",True,url)
                url = resp['location']
                print url
                for el in self.isomorphCheck(
                    "POST - create  new graph",
                    h,
                    url,
                    alternativeTestName="GET of POST - create  new graph"):
                    yield el

                h = httplib2.Http()
                for el in self.graphSubmit(
                    h,
                    url,
                    "POST - empty graph to existing graph",
                    expectedStatus=204):
                    yield el

                for el in self.isomorphCheck(
                    "POST - create  new graph",
                    h,
                    url,
                    alternativeTestName="GET of POST - after noop"):
                    yield el
            else:
                yield self.yieldResultElem(
                    testName,
                    False,
                    url,
                    u'POST to graph store should return Location header: %s'%repr(resp)
                )

@simple_service('POST', SERVICE_ID, 'gsp.validator.run',HTML_IMT+';charset=utf-8')
@xslt_rest(
    os.path.join(
        config().get('demo_path'),
        'gsp_validation_results.xslt'))
def validation(body, ctype):
    form = cgi.FieldStorage(
        fp=StringIO(body),
        environ=request.environ
    )
    validator = GraphStoreValidator(form.getvalue("gs_url"))
    src = StringIO()
    w = structwriter(indent=u"yes", stream=src)
    w.feed(
        ROOT(
            E(
                (TEST_NS,u'Results'),
                (elem for elem in validator.runTests())
            )
        )
    )
    return src.getvalue(), {
        u'project'  : form.getvalue("doap_project_name"),
        u'url'      : form.getvalue("gs_url")}
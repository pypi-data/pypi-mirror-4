# -*- coding: utf-8 -*-
import httplib2, os,cgi,urllib2,datetime
from akara                          import request, logger, module_config as config
from rdflib                         import URIRef
from rdflib.Graph                   import Graph
from rdflib_tools.GraphIsomorphism  import IsomorphicTestableGraph
from amara.lib                      import iri
from amara.lib.util                 import *
from amara.xslt                     import transform
from amara.writers.struct           import structwriter, E, NS, ROOT, RAW
from akara.services                 import simple_service, service
from akara                          import response
from akamu.xslt                     import xslt_rest, NOOPXML
from akamu.config.dataset           import GetParameterizedQuery
from akamu.diglot                   import layercake_mimetypes, XML_MT, layercake_parse_mimetypes
from cStringIO                      import StringIO
from urlparse                       import urlparse
from webob                          import Request

XHTML_IMT  = 'application/xhtml+xml'
HTML_IMT   = 'text/html'
XML_IMT    = 'application/xml'
SERVICE_ID = 'http://code.google.com/p/akamu/wiki/GraphStoreProtocol'
TEST_NS    = 'http://www.w3.org/2009/sparql/docs/tests/data-sparql11/http-rdf-update/tests.html'

@simple_service('GET', SERVICE_ID, 'gsp.validator.form',HTML_IMT+';charset=utf-8')
@xslt_rest(
    os.path.join(
        config().get('demo_path'),
        'gsp_validator.xslt'))
def validator_form(message=None):
    if message:
        return NOOPXML, { u'message':message }
    else:
        return NOOPXML

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
    "GET of replacement for empty graph",
    "PUT - replace empty graph",
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

GRAPH7=\
u"""<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf ="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:v   ="http://www.w3.org/2006/vcard/ns#"
    >
    <foaf:Person rdf:about="%s">
        <foaf:name>%s</foaf:name>
        <foaf:givenName>Jane</foaf:givenName>
        <foaf:familyName>Doe</foaf:familyName>
        <foaf:businessCard>
            <v:VCard>
                <v:fn>%s</v:fn>
            </v:VCard>
        </foaf:businessCard>
    </foaf:Person>
</rdf:RDF>"""

TEST_GRAPHS = {
    "PUT - Initial state"                   : (GRAPH1,"person/1",'xml',"John Doe"),
    "PUT - graph already in store"          : (GRAPH1,"person/1",'xml',"Jane Doe"),
    "PUT - default graph"                   : (GRAPH2,"",'xml',"Alice"),
    "PUT - mismatched payload"              : (GRAPH1,"person/1",'xml',"Jane Doe"),
    "PUT - empty graph"                     : (None,None,None,None),
    "PUT - replace empty graph"             : (GRAPH2,"",'xml',"Alice"),
    "POST - existing graph"                 : (GRAPH3,"person/1","xml","Jane Doe"),
    "HEAD on an existing graph"             : (GRAPH1,"person/1",'xml',"John Doe"),
    "HEAD on a non-existing graph"          : (None,None,None,None),
    "GET of POST - existing graph"          : (GRAPH4,"person/1","xml",("Jane Doe",)*2),
    "POST - create  new graph"              : (GRAPH2,"",'xml',"Alice"),
    "POST - empty graph to existing graph"  : (None,None,None,None),
    "multipart/form-data graph 1"           : (GRAPH5,"person/1",'xml',"Doe"),
    "multipart/form-data graph 2"           : (GRAPH6,"person/1",'xml',"Jane"),
    "GET of POST - multipart/form-data"     : (GRAPH7,"person/1",'xml',("Jane Doe",)*2)
}

class GraphStoreValidator(object):
    def __init__(self,graph_store_url,gs_url_internal):
        self.gs_url_internal = gs_url_internal
        if gs_url_internal:
            self.gs_url_internal = gs_url_internal\
            if gs_url_internal[-1] == '/' else gs_url_internal + '/'
        self.graph_store_url = graph_store_url
        self.graphs = TEST_GRAPHS.copy()
        self.graph_store_url_base = graph_store_url \
            if graph_store_url[-1] == '/' else graph_store_url + '/'

        for testName,(src,relUrl,format,name) in list(TEST_GRAPHS.items()):
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

        assert testName in TESTS, testName
        testId = testName.replace(' ','_').replace('-','').replace('/','_').lower()
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
            expectedStatus=[201,204],
            imt='text/turtle; charset=utf-8',
            format='n3',
            method='PUT',
            responseInfo=None,
            getUrl=None):
        responseInfo = responseInfo if responseInfo is not None else []
        graph = self.graphs[testName]
        body = graph.serialize(format=format) if graph is not None else u""
        hasPayload = False
        headers = {'cache-control'  : 'no-cache'}
        if method in ['PUT','POST']:
            hasPayload = True
            headers['content-type']   = imt
            headers['content-length'] = str(len(body))
        resp, content = h.request(
            url,
            method,
            body=body if hasPayload else None,
            headers=headers
        )
        responseInfo.append((resp,content))

        if isinstance(expectedStatus,list):
            matchingStatus = resp.status in expectedStatus
        else:
            matchingStatus = resp.status == expectedStatus

        if method == 'HEAD':
            if content:
                yield self.yieldResultElem(
                    testName,
                    False,
                    url,
                    u'HEAD response should have no content in the body'
                )
            elif not matchingStatus:
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
            elif 'content-length' not in resp:
                yield self.yieldResultElem(
                    testName,
                    False,
                    url,
                    u'expected content-length header in response'
                )
            elif 'content-type' not in resp:
                yield self.yieldResultElem(
                    testName,
                    False,
                    url,
                    u'expected content-type header in response'
                )
            else:
                yield self.yieldResultElem(testName,True,url)
        elif not matchingStatus:
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
            _url = getUrl if getUrl else url
            for el in self.isomorphCheck(testName,h,_url,getTestName):
                yield el

    def isomorphCheck(self,testName,h,url,alternativeTestName=None):
        try:
            resp, content = h.request(url,"GET",headers={
                'cache-control': 'no-cache',
                'Accept'       : 'text/turtle; charset=utf-8'
            })
        except:
            yield self.yieldResultElem(
                testName,
                False,
                url,
                u'Unable to perform content negotiated GET'%repr(e)
            )
        else:
            getTestName = alternativeTestName if alternativeTestName else testName
            if resp.status == 200:
                if 'content-type' not in resp or resp['content-type'].find('text/turtle')+1:
                    if content is not None and not content.strip():
                        content = None
                    g1=IsomorphicTestableGraph().parse(
                        StringIO(content),
                        format='n3') if content is not None else None
                    if g1 != self.graphs[testName]:
                        print "Unexpected response: "
                        print content
                        print resp.status
                        print resp
                        print "----"*5
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
                        u'expected returned content-type of "text/turtle; charset=utf-8", received %s'%(
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
        url          = iri.absolutize("person/1.ttl",self.graph_store_url_base)
        if self.gs_url_internal:
            internal_url = iri.absolutize("person/1.ttl",self.gs_url_internal)
            indirect_url = self.graph_store_url_base + '?graph=' + urllib2.quote(internal_url)
        else:
            indirect_url = self.graph_store_url_base + '?graph=' + urllib2.quote(url)

        for el in self.graphSubmit(h,url,"PUT - Initial state","GET of PUT - Initial state"):
            yield el

        h = httplib2.Http()
        url      = iri.absolutize("person/1.ttl",self.graph_store_url_base)
        testName = "HEAD on an existing graph"
        for el in self.graphSubmit(h,url,testName,expectedStatus=[200,204],method='HEAD'):
            yield el

        h = httplib2.Http()
        testName = "HEAD on a non-existing graph"
        resp, content = h.request(
            iri.absolutize("person/4.ttl",
                self.graph_store_url_base),
            "HEAD"
        )
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

        testName = u"PUT - graph already in store"
        for el in self.graphSubmit(
                            h,
                            url,
                            testName,
                            expectedStatus=[200,204],
                            getTestName="GET of PUT - graph already in store",
                            getUrl=indirect_url):
            yield el

        url = self.graph_store_url_base+'?default'
        testName = "PUT - default graph"
        for el in self.graphSubmit(
                            h,
                            url,
                            testName,
                            "GET of PUT - default graph",
                            expectedStatus=204):
            yield el

        h = httplib2.Http()
        url      = iri.absolutize("person/1.ttl",self.graph_store_url_base)
        testName = "PUT - mismatched payload"
        for el in self.graphSubmit(h,url,testName,expectedStatus=400,imt='application/rdf+xml'):
            yield el

        h = httplib2.Http()
        url          = iri.absolutize("person/2.ttl",self.graph_store_url_base)
        if self.gs_url_internal:
            internal_url = iri.absolutize("person/2.ttl",self.gs_url_internal)
            indirect_url = self.graph_store_url_base + '?graph=' + urllib2.quote(internal_url)
        else:
            indirect_url = self.graph_store_url_base + '?graph=' + urllib2.quote(url)

        for el in self.graphSubmit(
                            h,
                            indirect_url,
                            "PUT - empty graph",
                            "GET of PUT - empty graph",
                            getUrl=url):
            yield el

        h = httplib2.Http()
        url      = iri.absolutize("person/2.ttl",self.graph_store_url_base)
        for el in self.graphSubmit(
            h,
            url,
            "PUT - replace empty graph",
            "GET of replacement for empty graph",
            expectedStatus=[201,204]):
            yield el

        testName = "DELETE - existing graph"
        resp, content = h.request(url,"DELETE")
        if resp.status not in  [200,204]:
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
        for el in self.graphSubmit(
            h,
            url,
            testName,
            expectedStatus=[200,204],
            method='POST'):
            yield el
        for el in self.isomorphCheck(
            "GET of POST - existing graph",
            h,
            url,
            alternativeTestName="GET of POST - existing graph"):
            yield el

        try:
            from poster.encode import multipart_encode, MultipartParam
            from poster.streaminghttp import register_openers
            h = httplib2.Http()
            testName = "POST - multipart/form-data"

            register_openers()

            datagen, headers = multipart_encode(
                [
                    MultipartParam(
                        "lastName.ttl",
                        self.graphs["multipart/form-data graph 1"].serialize(
                            format='turtle'
                        ),
                        filename="lastName.ttl",
                        filetype='text/turtle; charset=utf-8'
                    ),
                    MultipartParam(
                        "firstName.ttl",
                        self.graphs["multipart/form-data graph 2"].serialize(
                            format='turtle'
                        ),
                        filename="firstName.ttl",
                        filetype='text/turtle; charset=utf-8'
                    )
                ]
            )

            req = urllib2.Request(url, datagen, headers)
            resp = urllib2.urlopen(req)

            if resp.code not in [200,204]:
                yield self.yieldResultElem(
                    testName,
                    False,
                    url,
                    u'expected status %s, received %s (%s)'%(
                        [200,204],
                        resp.code,
                        resp.read()
                    )
                )
            else:
                yield self.yieldResultElem(testName,True,url)
            for el in self.isomorphCheck(
                            "GET of POST - multipart/form-data",
                            h,
                            url,
                            "GET of POST - multipart/form-data"):
                yield el
        except urllib2.HTTPError, e:
            yield self.yieldResultElem(
                testName,
                False,
                url,
                u'Invalid Server response: %s'%repr(e)
            )
        except ImportError:
            pass

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
                yield self.yieldResultElem(testName,True,url)
                url = resp['location']
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
                    expectedStatus=[200,204],
                    method='POST'):
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

class WsgiGSPValidator(object):
    def __init__(self,app): pass
    def __call__(self, environ, start_response):
        req = Request(environ)
        if req.method == 'POST':
            if req.content_type == 'application/x-www-form-urlencoded':
                implementation_url = req.POST.get('doap_project_url')
                validator_url      = req.POST.get('gs_url')
                project_name       = req.POST.get('doap_project_name')
                gsInternalUrl      = req.POST.get('gs_url_internal')
            else:
                form = cgi.FieldStorage(
                    fp=StringIO(req.body),
                    environ=request.environ
                )
                implementation_url = form.getvalue("doap_project_url")
                validator_url      = form.getvalue("gs_url")
                project_name       = form.getvalue('doap_project_name')
                gsInternalUrl      = form.getvalue('gs_url_internal')
        elif req.method == 'GET':
            implementation_url = req.params.get('doap_project_url')
            validator_url      = req.params.get("gs_url")
            project_name       = req.params.get('doap_project_name')
            gsInternalUrl      = req.params.get('gs_url_internal')
        else:
            rt = "Validation HTTP methods supported are POST and GET: received %s"%(
                req.method
            )
            start_response("405 Method Not Allowed",
                [("Content-Length",  len(rt))])
            return rt
        if validator_url and implementation_url:
            validator = GraphStoreValidator(validator_url,gsInternalUrl)
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
            requestedRDF = set(layercake_mimetypes).intersection(req.accept)
            if 'HTTP_ACCEPT' not in environ or not requestedRDF:
                rt = transform(
                    src.getvalue(),
                    os.path.join(
                        config().get('demo_path'),
                        'gsp_validation_results.xslt'),
                    params={
                        u'project'  : project_name,
                        u'url'      : implementation_url})
                start_response("200 Ok",
                    [("Content-Type"  , HTML_IMT+';charset=utf-8'),
                     ("Content-Length",  len(rt))])
                return rt
            elif requestedRDF:
                preferredMT = req.accept.best_match(layercake_mimetypes)
                format = layercake_mimetypes[preferredMT]
                rt = transform(
                    src.getvalue(),
                    os.path.join(
                        config().get('demo_path'),
                        'gsp_validation_results_earl.xslt'),
                    params={
                        u'project'  : project_name,
                        u'date'     : datetime.date.today().isoformat(),
                        u'url'      : implementation_url})
                g=Graph().parse(StringIO(rt),format='xml')
                g.bind('validator',URIRef('http://metacognition.info/gsp_validation/'))
                g.bind('gsp',URIRef('http://www.w3.org/2009/sparql/docs/tests/data-sparql11/http-rdf-update/manifest#'))
                g.bind('test',
                       URIRef(
                           'http://www.w3.org/2009/sparql/docs/tests/data-sparql11/http-rdf-update/#')
                )
                rt=g.serialize(format=format)
                start_response("200 Ok",
                    [("Content-Type"  , preferredMT),
                     ("Content-Length",  len(rt))])
                return rt
        else:
            msg="Bad request"
            start_response("303 See Other",
                [("Location","gsp.validator.form?message=Please+provide+a+Graph+Store+URL+to+validate+and+an+implementation+url"),
                 ("Content-Length",  len(msg))])
            return msg

@service(SERVICE_ID, 'gsp.validator.run',wsgi_wrapper=WsgiGSPValidator)
def validation():pass
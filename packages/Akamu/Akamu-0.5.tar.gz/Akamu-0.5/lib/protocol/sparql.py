__author__ = 'chimezieogbuji'

import os, string, random, pyparsing, time
from cStringIO            import StringIO
from webob                import Request
try:
    from Triclops.Server  import WsgiApplication, SD_FORMATS, MIME_SERIALIZATIONS
except ImportError: pass
from akamu.config.dataset import ConnectToDataset, GetGraphStoreForProtocol, ConfigureTriclops, GetExternalGraphStoreURL
from akamu.diglot         import layercake_mimetypes, XML_MT, layercake_parse_mimetypes
from amara.lib            import iri
from wsgiref.util         import shift_path_info, request_uri
from rdflib.Graph         import Graph,ConjunctiveGraph
from rdflib.sparql.parser import parse
from rdflib               import OWL, RDF, RDFS, URIRef, BNode, Namespace, Literal

DefaultGraph_NS = Namespace('tag:metacognition.info,2012:DefaultGraphs#')

def random_filename(chars=string.hexdigits, length=16, prefix='',
                    suffix='', verify=True, attempts=10):
    """
    From - http://ltslashgt.com/2007/07/23/random-filenames/
    """
    for attempt in range(attempts):
        filename = ''.join([random.choice(chars) for i in range(length)])
        filename = prefix + filename + suffix
        if not verify or not os.path.exists(filename):
            return filename

class NoEmptyGraphSupport(Exception):
    def __init__(self):
        super(NoEmptyGraphSupport, self).__init__(
            "Implementation does not support empty graphs"
        )

def RequestedGraphContent(req,store,datasetName):
    graphParamValue = req.params.get('graph')
    if 'default' in req.params:
        graph = Graph(identifier=DefaultGraph_NS[datasetName],store=store)
    else:
        graphIri        = graphParamValue if graphParamValue else req.url
        graph           = Graph(identifier=URIRef(graphIri),store=store)
    return graph

def HandleGET(req,environ,start_response,store,datasetName):
    graph           = RequestedGraphContent(req,store,datasetName)
    if not graph and 'default' not in req.params:
        raise NoEmptyGraphSupport()

    requestedRDF = req.accept.best_match(list(layercake_mimetypes))
    if 'HTTP_ACCEPT' not in environ or not requestedRDF:
        requestedMT = 'application/rdf+xml'
        format      = 'application/rdf+xml'
    elif requestedRDF:
        preferredMT = req.accept.best_match(layercake_mimetypes)
        requestedMT = preferredMT
        format = layercake_mimetypes[preferredMT]
    content = graph.serialize(format=format)
    start_response("200 Ok",
        [("Content-Type"  , requestedMT),
         ("Content-Length", len(content))]
    )
    return content

def HandlePUT(req,start_response,store,datasetName):
    graph           = RequestedGraphContent(req,store,datasetName)
    nonexistent = not graph and 'default' not in req.params
    if not req.content_type:
        rt = "Didn't provide an RDF Content-type header"
        start_response("400 Bad Request",
            [("Content-Length",  len(rt))])
        return rt
    else:
        format = layercake_parse_mimetypes.get(
            req.content_type,
            layercake_mimetypes[req.content_type])
        try:
            payloadGraph = Graph().parse(StringIO(req.body),format = format)
        except Exception, e:
            rt = e.message
            start_response("400 Bad Request",
                [("Content-Length",  len(rt))])
            return rt
    if payloadGraph:
        graph.remove((None,None,None))
        for s,p,o in payloadGraph:
            graph.add((s,p,o))
        store.commit()
        if nonexistent:
            start_response("201 Created",[])
        else:
            start_response("204 No Content",[])
        return ""
    else:
        #Empty graph
#        raise NoEmptyGraphSupport()
        start_response("200 Ok",[])
        return "NOOP: server doesn't support empty graphs"

def HandleDELETE(req,start_response,store,datasetName):
    graph           = RequestedGraphContent(req,store,datasetName)
    if not graph and 'default' not in req.params:
        raise NoEmptyGraphSupport()
    else:
        graph.remove((None,None,None))
        store.commit()
        start_response("200 Ok",[])
        return ""

def handleTrailingSlash(url,strip=True):
    if strip:
        return url if url[-1]!='/' else url[:-1]
    else:
        return url+'/' if url[-1]!='/' else url

def HandlePOST(req,start_response,store,graphStore,externalGS,datasetName):
    graph           = RequestedGraphContent(req,store,datasetName)

    if not req.content_type:
        rt = "Didn't provide an RDF Content-type header"
        start_response("400 Bad Request",
            [("Content-Length",  len(rt))])
        return rt
    if handleTrailingSlash(req.url) == handleTrailingSlash(graphStore):
        #If the request IRI identifies the underlying Graph Store, the origin
        #server MUST create a new RDF graph comprised of the statements in
        #the RDF payload and return a designated graph IRI associated with
        #the new graph. The new graph IRI should be specified in the Location
        #HTTP header along with a 201 Created code and be different from the
        #request IRI.
        new_filename = random_filename(suffix=req.params.get('suffix',''))

        new_location = iri.absolutize(
            new_filename,
            handleTrailingSlash(graphStore,strip=False)
        )
        new_location = URIRef(new_location)

        external_new_location = iri.absolutize(
            new_filename,
            handleTrailingSlash(
                externalGS if externalGS else graphStore,
                strip=False)
        )

        try:
            Graph(identifier=new_location,store=store).parse(
                StringIO(req.body),
                format   = layercake_parse_mimetypes[req.content_type]
            )
        except Exception, e:
            rt = e.message
            start_response("400 Bad Request",
                [("Content-Length",  len(rt))])
            return rt
        store.commit()
        start_response("201 Created",
            [("Location", external_new_location),
             ("Content-Length",  0)])
        return ''
    else:
        if req.content_type == 'multipart/form-data':
            import cgi
            form = cgi.FieldStorage(
                fp=StringIO(body),
                environ=request.environ
            )
            print form
            print cgi.parse_multipart(StringIO(req.body), {})
            raise NotImplementedError("Not yet implemented")
        else:
            toAdd    = []
            canMerge = True
            try:
                for triple in Graph().parse(
                    StringIO(req.body),
                    format   = layercake_parse_mimetypes[req.content_type]
                ):
                    s,p,o = triple
                    if triple not in graph:
                        toAdd.append((s,p,o,graph))
                    elif [term for term in triple if isinstance(term,BNode)]:
                        #Blank node in common is shared, no support for this currently
                        #See: http://www.w3.org/TR/rdf-mt/#defmerge
                        canMerge = False
                        break
            except Exception, e:
                rt = str(e)
                start_response("400 Bad Request",
                    [("Content-Length",  len(rt))])
                return rt
            if not canMerge:
                rt = "Merge involving shared blank nodes not supported"
                start_response("409 Conflict",
                    [("Content-Length",  len(rt))])
                return rt
            else:
                graph.addN(toAdd)
                store.commit()
                start_response("200 Ok",[])
                return ''

class graph_store_protocol(object):
    """

    """
    def __init__(self):
        self.datasetName,self.gs_url = GetGraphStoreForProtocol()
        self.store                   = ConnectToDataset(self.datasetName)
        self.external_gs_url         = GetExternalGraphStoreURL()

    def __call__(self, func):
        def innerHandler(environ, start_response):
            req = Request(environ)
            try:
                if req.method   in ['HEAD','GET']:
                    rt = HandleGET(req,environ,start_response,self.store,self.datasetName)
                    if req.method == 'GET':
                        return rt
                    else:
                        return ''
                elif req.method == 'PUT':
                    return HandlePUT(req,start_response,self.store,self.datasetName)
                elif req.method == 'DELETE':
                    return HandleDELETE(req,start_response,self.store,self.datasetName)
                elif req.method == 'PATCH':
                    rt="PATCH not supported"
                    start_response("405 Method Not Allowed",
                        [("Content-Length",  len(rt))]
                    )
                    return rt
                elif req.method == 'POST':
                    return HandlePOST(
                        req,
                        start_response,
                        self.store,
                        self.gs_url,
                        self.external_gs_url,
                        self.datasetName)
                else:
                    start_response("405 Method Not Allowed",[])
                    return "Method not allowed for this resource"
            except NoEmptyGraphSupport, e:
                rt = "Implementation does not support empty graphs"
                start_response("404 Method Not Allowed",
                    [("Content-Length",  len(rt))])
                return rt
            except NotImplementedError, e:
                raise e
        return innerHandler

class sparql_rdf_protocol(object):
    """
    Prepares a Triclops WSGI application for use to wrap
     the Akara via the 'wsgi_wrapper' keyword argument of
     @simple_service and @service

    See: http://code.google.com/p/python-dlp/wiki/Triclops
    """
    def __init__(self, root, datasetName):
        self.nsBindings    = {  u'owl' :OWL.OWLNS,
                                u'rdf' :RDF.RDFNS,
                                u'rdfs':RDFS.RDFSNS}
        self.litProps = set()
        self.resProps = set()
        self.root               = root
        self.datasetName        = datasetName
        self.conf               = ConfigureTriclops(
                                    self.datasetName,
                                    self.nsBindings,
                                    self.litProps,
                                    self.resProps)
        self.conf['endpoint']   = self.root

    def __call__(self, func):

        def innerHandler(environ, start_response):
            # @@@ Core Application @@@
            app = WsgiApplication(
                self.conf,
                self.nsBindings,
                [],
                self.litProps,
                self.resProps,
                Graph(),
                Graph(),
                set(),
                Graph())

            request = Request(environ)
            d                 = request.params
            query             = d.get('query')
            ticket            = d.get('ticket')
            default_graph_uri = d.get('default-graph-uri')
            rtFormat          = d.get('resultFormat')
            print "## Query ##\n", query, "\n###########"
            print "Default graph uri ", default_graph_uri

            if request.method == 'POST':
                if request.content_type == 'application/sparql-query':
                    query = request.content_type
                elif request.content_type == 'application/x-www-form-urlencoded':
                    query = request.POST.get('query')

            requestedFormat = environ.get('HTTP_ACCEPT','application/rdf+xml')

            if request.method == 'POST':
                assert query,"POST can only take an encoded query or a query in the body"
            elif request.method == 'GET' and not query:
                if requestedFormat not in SD_FORMATS:
                    requestedFormat = 'application/rdf+xml'
                if app.ignoreQueryDataset:
                    targetGraph = app.buildGraph(default_graph_uri)
                else:
                    targetGraph = app.buildGraph(default_graph_uri=None)

                sdGraph = Graph()

                SD_NS  = Namespace('http://www.w3.org/ns/sparql-service-description#')
                SCOVO  = Namespace('http://purl.org/NET/scovo#')
                VOID   = Namespace('http://rdfs.org/ns/void#')
                FORMAT = Namespace('http://www.w3.org/ns/formats/')

                sdGraph.bind(u'sd',SD_NS)
                sdGraph.bind(u'scovo',SCOVO)
                sdGraph.bind(u'void',VOID)
                sdGraph.bind(u'format',FORMAT)

                service     = BNode()
                datasetNode = BNode()
                if app.endpointURL:
                    sdGraph.add((service,SD_NS.endpoint,URIRef(app.endpointURL)))
                sdGraph.add((service,SD_NS.supportedLanguage        ,SD_NS.SPARQL10Query))
                sdGraph.add((service,RDF.type                       ,SD_NS.Service))
                sdGraph.add((service,SD_NS.defaultDatasetDescription,datasetNode))
                sdGraph.add((service,SD_NS.resultFormat,FORMAT['SPARQL_Results_XML']))
                sdGraph.add((datasetNode,RDF.type,SD_NS.Dataset))

                for graph in targetGraph.store.contexts():
                    graphNode  = BNode()
                    graphNode2 = BNode()
                    sdGraph.add((datasetNode,SD_NS.namedGraph,graphNode))
                    sdGraph.add((graphNode,SD_NS.name,URIRef(graph.identifier)))
                    sdGraph.add((graphNode,SD_NS.graph,graphNode2))
                    sdGraph.add((graphNode,RDF.type,SD_NS.NamedGraph))
                    sdGraph.add((graphNode2,RDF.type,SD_NS.Graph))
                    noTriples = Literal(len(graph))
                    sdGraph.add((graphNode2,VOID.triples,noTriples))
                doc = sdGraph.serialize(
                    format=MIME_SERIALIZATIONS[requestedFormat])
                status = '200 OK'
                response_headers = [
                    ('Content-type'  , requestedFormat),
                    ('Content-Length', len(doc))
                ]
                start_response(status,response_headers)
                return doc
            else:
                assert request.method == 'GET',"Either POST or GET method!"
            if app.ignoreQueryDataset:
                app.targetGraph = app.buildGraph(default_graph_uri)
            else:
                app.targetGraph = app.buildGraph(default_graph_uri=None)

            for pref,nsUri in app.nsBindings.items():
                app.targetGraph.bind(pref,nsUri)

            origQuery = query
            try:
                query=parse(query)
            except pyparsing.ParseException, e:
                rt = "Malformed SPARQL Query: %s"%repr(e)
                status = '400 Bad Request'
                response_headers = [('Content-type','text/html'),
                                    ('Content-Length',
                                     len(rt))]
                start_response(status,response_headers)
                return rt

            start = time.time()

            if app.ignoreBase and hasattr(query,'prolog') and query.prolog:
                query.prolog.baseDeclaration=None
            if app.ignoreQueryDataset and hasattr(query.query,'dataSets') and query.query.dataSets:
                print "Ignoring query-specified datasets: ", query.query.dataSets
                query.query.dataSets = []

            if not app.proxy and ticket:
                #Add entry for current thread in ticket -> thread id lookup
                global ticketLookup
                ticketLookup[ticket]=app.targetGraph.store._db.thread_id()

                #Run the actual query
            rt = app.targetGraph.query(origQuery,
                initNs=app.nsBindings,
                DEBUG=app.debugQuery,
                parsedQuery=query)
            print "Time to execute SPARQL query: ", time.time() - start
            qRT = rt.serialize(format='xml')
            app.targetGraph.close()
            print "Time to execute and seralize SPARQL query: ", time.time() - start
            print "# of bindings: ", rt.noAnswers

            if rtFormat in ['xml','csv'] or not rtFormat:

                rtDoc = NonvalidatingReader.parseString(qRT,
                    'tag:nobody@nowhere:2007:meaninglessURI')
                stylesheetPath = rtFormat == 'xml' and '/xslt/xml-to-html.xslt' or '/xslt/xml-to-csv.xslt'
                imt='application/xml'

                pi = rtDoc.createProcessingInstruction("xml-stylesheet",
                    "type='text/xml' href='%s'"%stylesheetPath)
                #Add a stylesheet instruction to direct browsers how to render the result document
                rtDoc.insertBefore(pi, rtDoc.documentElement)
                out = StringIO()
                PrettyPrint(rtDoc, stream=out)
                rt = out.getvalue()
            elif rtFormat == 'csv-pure':
                imt='text/plain'
                rt=app.csvProcessor.run(InputSource.DefaultFactory.fromString(qRT))

            status = '200 OK'
            response_headers = [('Content-type',imt),
                                ('Content-Length',len(rt))]
            start_response(status, response_headers)
            return rt
        return innerHandler


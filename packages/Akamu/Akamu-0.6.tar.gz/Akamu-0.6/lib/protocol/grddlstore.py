__author__ = 'chimezieogbuji'

import os, imp, random, string, datetime, hashlib
from cStringIO import StringIO
from akamu.config.diglot import GetDiglotManager
from akamu.diglot import layercake_mimetypes, XML_MT, GetFNameFromPath
from wsgiref.util import shift_path_info, request_uri
from akara import request
from amara.lib import U, inputsource
from webob import Request
from amara.xslt  import transform
from amara.bindery import parse
from amara.xupdate import reader, XUpdateError, apply_xupdate
from rdflib import URIRef
from rdflib.Graph import Graph
from akamu.config.dataset import ConnectToDataset
from akamu.wheezy import WheezyCachingAdapterSetup

GRDDL_NS   = u'http://www.w3.org/2003/g/data-view#'
XUPDATE_NS = u'http://www.xmldb.org/xupdate'

XSLT_MT    = u'application/xslt+xml'

def updatePolicy4File(filePath,policy):
    mtime_dt = datetime.datetime.fromtimestamp(os.path.getmtime(filePath))
    policy.last_modified(mtime_dt)
    policy.etag(hashlib.sha1(open(filePath).read()).hexdigest())

def HandleGET(req,mgr,environ,root,start_response):
    path = request_uri(environ,0).split(root)[-1]
    res = mgr.getResource(path)
    content = res.getContent()
    requestedXML = XML_MT in req.accept
    requestedRDF = req.accept.best_match(list(layercake_mimetypes))
    if 'HTTP_ACCEPT' not in environ or (requestedXML and not requestedRDF):
        start_response("200 Ok",
            [("Content-Type", XML_MT),
             ("Content-Length", len(content))]
        )
        return content
    elif requestedRDF and requestedXML:
        #requested both RDF media types and POX
        doc=parse(content)
        docRoot = doc.xml_select('/*')[0]

        transformPath = os.path.join(root,mgr.findTransform(path)[1:])
        docRoot.xmlns_attributes[u'grddl'] = GRDDL_NS
        docRoot.xml_attributes[(GRDDL_NS,u'transformation')] = transformPath
        stream = StringIO()
        doc.xml_write(stream=stream)
        rt = stream.getvalue()
        start_response("200 Ok",
            [("Content-Type", XML_MT),
             ("Content-Length", len(rt))]
        )
        return rt
    elif requestedRDF:
        store = ConnectToDataset(mgr.datasetName)
        preferredMT = req.accept.best_match(layercake_mimetypes)
        graphUri = URIRef(
            mgr.graphUriFn(
                path,
                GetFNameFromPath(path))
        )
        rt = Graph(store,identifier=graphUri).serialize(layercake_mimetypes[preferredMT])
        start_response("200 Ok",
            [("Content-Type", preferredMT),
             ("Content-Length", len(rt))]
        )
        return rt
    else:
        raise

def HandlePATCH(req,mgr,environ,root,start_response):
    path = request_uri(environ,0).split(root)[-1]
    res = mgr.getResource(path)
    content = res.getContent()

    if req.content_type == XSLT_MT:
        newContent = transform(content,req.body)
        res.update(newContent)
        start_response("200 Ok",[])
        return ''
    else:
        payloadDoc = parse(req.body)
        if payloadDoc.xml_select('/xu:modifications',prefixes={u'xu' : XUPDATE_NS}):
            from amara.xupdate import reader, XUpdateError, apply_xupdate
            from amara.lib import inputsource
            source     = inputsource( content, 'source')
            xupdate    = inputsource(req.body, 'xupdate-source')
            newContent = apply_xupdate(source, xupdate)
            rt=StringIO()
            newContent.xml_write(stream=rt)
            res.update(rt.getvalue())
            start_response("200 Ok",[])
            return ''
        else:
            rt = 'PATCH body must be XSLT (application/xslt+xml) or XUpdate'
            start_response("400 Bad Request",
                [("Content-Length",  len(rt))])
            return rt

def HandlePOST(req,mgr,diglotPath,base=None):
    targetContent = mgr.getResource(diglotPath).getContent()

    if req.content_type == XML_MT:
        #@TODO: handle parameters
        return transform(req.body,targetContent), 'application/xml+rdf'
    else:
        doc=parse(targetContent)
        payloadGraph = Graph().parse(
            StringIO(req.body),
            format   = layercake_mimetypes[req.content_type],
            publicID = URIRef(base) if base else None
        )
        for revXFormSrc in doc.xml_select(
            '/xsl:stylesheet/ggs:reverse_transform',prefixes={
                u'ggs': u'http://code.google.com/p/akamu/wiki/DiglotFileSystemProtocol#Bidirectional_transformations',
                u'xsl': u'http://www.w3.org/1999/XSL/Transform'}):
            fnCode = revXFormSrc.xml_select('string(text())').strip()
            module = imp.new_module('inverseMap')
            exec fnCode in module.__dict__
            return module.ReverseTransform(payloadGraph), XML_MT

def HandleDirectoryPOST(req,start_response,mgr,newPath,newDiglotPath):
    if req.content_type == XML_MT:
        mgr.createResource(newPath,req.body)
        start_response("201 Created",
            [("Location", newDiglotPath),
                ("Content-Length",  0)])
        return ''
    else:
        requestedRDF = req.accept.best_match(list(layercake_mimetypes))
        if not requestedRDF:
            rt = "Didn't provide an RDF Content-type header"
            start_response("400 Bad Request",
                [("Content-Length",  len(rt))])
            return rt
        else:
            base = req.GET.get('base')
            payloadGraph = Graph().parse(
                StringIO(req.body),
                format   = layercake_mimetypes[req.content_type],
                publicID = URIRef(base) if base else None
            )
            xform = mgr.findTransform(newPath)
            targetContent = mgr.getResource(xform).getContent()
            doc=parse(targetContent)

            revXForm = doc.xml_select(
                '/xsl:stylesheet/ggs:reverse_transform',prefixes={
                    u'ggs': u'http://code.google.com/p/akamu/wiki/DiglotFileSystemProtocol#Bidirectional_transformations',
                    u'xsl': u'http://www.w3.org/1999/XSL/Transform'})
            if revXForm:
                revXFormSrc = revXForm[0]
                fnCode = revXFormSrc.xml_select('string(text())').strip()
                module = imp.new_module('inverseMap')
                exec fnCode in module.__dict__
                xmlDoc = module.ReverseTransform(payloadGraph)
                mgr.createResource(newPath,xmlDoc)
                start_response("201 Created",
                    [("Location", newDiglotPath),
                        ("Content-Length",  0)])
                return ''
            else:
                rt = "Target XSLT doesn't have a reverse transform"
                start_response("400 Bad Request",
                [("Content-Length",  len(rt))])
                return rt

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

class xforms_grddl(object):
    """
    Decorator for service for an XForms documents
    that manage Diglot resources (served from a
    mounted Diglot Filesystem Protocol instance)

    Can be bound for use with a particular XForm document or
    the document used can be provided as a parameter to the
    service invokation.
    """
    def __init__(self,
                 instanceId='diglot-resource',
                 submissionId='diglot-submission',
                 hostDocumentBase=None,
                 hostDocument=None,
                 diglotRoot=None,
                 hostDocumentParam='document',
                 instanceAttribute='src',
                 instanceParam='src'):
        self.submissionId       = submissionId
        self.diglotRoot         = diglotRoot
        self.hostDocumentBase   = hostDocumentBase
        self.instanceParam      = instanceParam
        self.instanceId         = instanceId
        self.instanceAttribute  = instanceAttribute
        self.hostDocument       = hostDocument
        self.hostDocumentParam  = hostDocumentParam

    def __call__(self, func):
        def innerHandler(*args, **kwds):
            req = Request(request.environ)

            xformDocument = req.params.get(self.hostDocumentParam,self.hostDocument)
            xformDocument = os.path.join(
                self.hostDocumentBase,
                xformDocument) if self.hostDocumentBase else xformDocument

            instancePath = req.params[self.instanceParam]
            instancePath = os.path.join(
                self.diglotRoot,
                instancePath) if self.diglotRoot else instancePath

            updateSrc =\
            """<?xml version="1.0"?>
            <xupdate:modifications
                version="1.0"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns:xf="http://www.w3.org/2002/xforms"
                xmlns:xupdate="http://www.xmldb.org/xupdate">
                <xupdate:update select="/xhtml:html/xhtml:head/xf:model/xf:instance[@id = '%s']/@%s">%s</xupdate:update>
                <xupdate:update select="/xhtml:html/xhtml:head/xf:model/xf:submission[@id = '%s']/@resource">%s</xupdate:update>
            </xupdate:modifications>
            """%(
                    self.instanceId,
                    self.instanceAttribute,
                    instancePath,
                    self.submissionId,
                    instancePath
                )
            source      = inputsource(xformDocument, 'source')
            xupdate     = inputsource(updateSrc, 'xupdate-source')
            doc = apply_xupdate(source, xupdate)
            aStream = StringIO()
            doc.xml_write(stream=aStream)
            return aStream.getvalue()
        return innerHandler

class grddl_graphstore_resource(object):
    """
    Extension of SPARQL Graph Store Protocol for use with Diglot filesystem

    Payload are GRDDL source documents,
    GET requests without Accept headers or with an 'application/xml' Accept header
     returns the XML document, those with RDF media types and application/xml return
     GRDDL source documents with references to transformation for the directory, and
     Accept headers with RDF media types return the RDF faithful rendition of the
     Diglot resource.

     XML posted to transforms in the diglot system invoke the transformation of
     the document, returning the GRDDL result graph.  RDF posted to transforms
     with reverse mappings return the corresponding XML document

     XUpdate sent via HTTP PATCH request to diglot resources will be applied to them.
     Closed XSLT transforms sent via HTTP PATCH to diglot resources will also be applied,
     replacing them with the result

     HEAD requests, are the same as GET but without any returned content

     Mounts an implementation of the protocol at the specified root and using the
     given graphUriFn funciton for use with the manager

    """
    def __init__(self, root, graphUriFn, caching = False, cacheability = None):
        self.root         = root
        self.graphUriFn   = graphUriFn
        self.cachingSetup = WheezyCachingAdapterSetup(
            queries=['base'],
            environ=['HTTP_ACCEPT'],
            asFn = True
            ) if caching else None
        self.cachingSetup.name = 'wheezyApp'
        self.cacheability = cacheability if cacheability else 'public'

    def introspect_resource(self,req,mgr):
        diglotPath = req.path.split(self.root)[-1]
        isXslt = diglotPath in mgr.transforms4Dir.values()
        return diglotPath, isXslt

    def handleResourceCacheability(self,mgr,diglotPath,cacheability,environ):
        policy = environ['wheezy.http.HTTPCachePolicy'](cacheability)
        updatePolicy4File(
            mgr.getFullPath(diglotPath),
            policy
        )
        environ['wheezy.http.cache_policy']     = policy
        environ['wheezy.http.cache_dependency'] = diglotPath

    def invalidateResourceCache(self,cacheability,environ,diglotPath):
        policy = environ['wheezy.http.HTTPCachePolicy'](cacheability)
        environ['akamu.wheezy.invalidate'](diglotPath)
        environ['wheezy.http.cache_policy'] = policy

    def __call__(self, func):
        def innerHandler(environ, start_response):
            req = Request(environ)
            mgr = GetDiglotManager(self.graphUriFn)
            diglotPath, isXslt = self.introspect_resource(req,mgr)
            try:
                if req.method   in ['HEAD','GET']:
                    rt = HandleGET(req,mgr,environ,self.root,start_response)
                    if req.method == 'GET':
                        if self.cachingSetup:
                            self.handleResourceCacheability(
                                mgr,
                                diglotPath,
                                self.cacheability,
                                environ
                            )
                        return rt
                    else:
                        return ''
                elif req.method == 'PUT':
                    _path = mgr.getFullPath(diglotPath)
                    if not os.path.exists(_path):
                        mgr.createResource(diglotPath,req.body)
                        if self.cachingSetup: environ['wheezy.http.noCache'] = True
                        start_response("201 Created",[])
                    else:
                        mgr.getResource(diglotPath).update(req.body)
                        environ['wheezy.http.noCache'] = True
                        start_response("204 No Content",[])
                        if self.cachingSetup:
                            self.invalidateResourceCache(
                                self.cacheability,
                                environ,
                                diglotPath
                            )
                    return ''
                elif req.method == 'DELETE':
                    mgr.getResource(diglotPath).delete()
                    msg = '%s has been deleted'%diglotPath
                    start_response("204 No Content",
                        [("Content-Length",  len(msg))]
                    )
                    if self.cachingSetup:
                        self.invalidateResourceCache(
                            self.cacheability,
                            environ,
                            diglotPath
                        )
                        environ['wheezy.http.noCache'] = True
                    return msg
                elif req.method == 'PATCH':
                    rt = HandlePATCH(req,mgr,environ,self.root,start_response)
                    if self.cachingSetup:
                        self.invalidateResourceCache(
                            self.cacheability,
                            environ,
                            diglotPath
                        )
                        environ['wheezy.http.noCache'] = True
                    return rt
                elif req.method == 'POST' and isXslt:
                    rt,cont_type = HandlePOST(req,mgr,diglotPath,base=req.GET.get('base'))
                    start_response("200 Ok",
                        [("Content-Type"  , cont_type),
                         ("Content-Length",  len(rt))]
                    )
                    if self.cachingSetup: environ['wheezy.http.noCache'] = True
                    return rt
                elif req.method == 'POST' and os.path.isdir(mgr.getFullPath(diglotPath)):
                    randFileN = random_filename()+'.xml'
                    newPath       = os.path.join(diglotPath,randFileN)
                    newDiglotPath = os.path.join(self.root,diglotPath[1:],randFileN)
                    if self.cachingSetup: environ['wheezy.http.noCache'] = True
                    return HandleDirectoryPOST(
                        req,
                        start_response,
                        mgr,
                        newPath,
                        newDiglotPath
                    )
                else:
                    start_response("405 Method Not Allowed",[])
                    return "Method not allowed for this resource"
            except IOError, e:
                msg = str(e)#e.message
                start_response("404 Method Not Allowed",[("Content-Length",  len(msg))])
                return msg
        if self.cachingSetup:
            return self.cachingSetup(innerHandler)
        else:
            return innerHandler
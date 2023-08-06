import os
from cStringIO import StringIO
from akamu.config.dataset import ConnectToDataset, ReplaceGraph, ClearGraph
from amara.xslt  import transform
from rdflib.store import Store
from rdflib.Graph import Graph
from rdflib import URIRef

def GetFNameFromPath(path):
    return path.split('/')[-1]

layercake_mimetypes = {
    'application/rdf+xml' : 'xml',
    'text/n3'             : 'n3',
    'text/turtle'         : 'turtle',
    #'text/plain'          : 'nt'
}

layercake_parse_mimetypes = {
    'application/rdf+xml' : 'xml',
    'text/n3'             : 'n3',
    'text/turtle'         : 'n3',
    #'text/plain'          : 'nt'
}

XML_MT = 'application/xml'

class Manager(object):
    def __init__(self,root,datasetName=None,graphUriFn=None,transforms4Dir=None):
        self.root           = root
        self.datasetName    = datasetName
        self.graphUriFn     = graphUriFn
        self.transforms4Dir = transforms4Dir

    def hasResource(self,path):
        return os.path.exists(
            os.path.join(
                self.root,
                path[1:] if path[0] == '/' else path
            )
        )

    def getFullPath(self,path):
        return os.path.join(self.root,path[1:] if path[0] == '/' else path)

    def findTransform(self,path):
        parentDir = '/'.join(path.split('/')[:-1]) if path.find('/')+1 else '/'
        rootXform = self.transforms4Dir.get('/')
        xform     = self.transforms4Dir.get(parentDir)
        if xform:
            return xform
        elif len(path.split('/'))>1:
            return self.findTransform(parentDir)
        elif rootXform:
            return rootXform

    def synch(self,path=None,parameters=None):
        parameters = parameters if parameters else {}
        if path:
            graphUri = URIRef(self.graphUriFn(path,GetFNameFromPath(path)))
            params = {
                u'path'     : path,
                u'graph-uri': graphUri
            }
            params.update(parameters)

            xFormPath = self.findTransform(path)
            rt = transform(
                self.getResource(path).getContent(),
                self.getResource(xFormPath).getContent(),
                params=params
            )
            ReplaceGraph(
                self.datasetName,
                graphUri,
                StringIO(rt),
                format='xml',
                storeName=not isinstance(self.datasetName,Store),
                baseUri=graphUri
            )
        else:
            raise NotImplementedError("[..]")

    def getResource(self,path):
        return Resource(self,path)

    def deleteResource(self,path):
        self.getResource(path).delete()

    def createResource(self,path,content,parameters=None):
        parameters = parameters if parameters else {}
        res = Resource(self,path)
        res.update(content,parameters)
        return res

class Resource(object):
    def __init__(self,manager,path):
        self.manager = manager
        self.path    = path

    def delete(self):
        os.remove(self.manager.getFullPath(self.path))
        graphUri = URIRef(
            self.manager.graphUriFn(
                self.path,GetFNameFromPath(self.path))
        )
        ClearGraph(
            self.manager.datasetName,
            graphUri,
            storeName=not isinstance(self.manager.datasetName,Store))

    def update(self,content,parameters=None):
        parameters = parameters if parameters else {}
        f=open(self.manager.getFullPath(self.path),'w')
        f.write(content)
        f.close()
        self.manager.synch(self.path,parameters)

    def getContent(self,mediaType=None):
        if mediaType is None or mediaType == XML_MT:
            return open(self.manager.getFullPath(self.path)).read()
        else:
            store = ConnectToDataset(self.manager.datasetName)
            graphUri = URIRef(self.manager.graphUriFn(self.path,GetFNameFromPath(path)))
            graph = Graph(store,identifier=graphUri)
            return graph.serialize(format=layercake_mimetypes[mediaType])
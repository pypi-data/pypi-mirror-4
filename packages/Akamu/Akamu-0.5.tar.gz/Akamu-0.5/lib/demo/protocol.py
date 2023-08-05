__author__ = 'chimezieogbuji'

from akara.services import simple_service, service
from akamu.protocol.grddlstore import grddl_graphstore_resource

SERVICE_ID = 'http://code.google.com/p/akamu/wiki/DiglotFileSystemProtocol'

def TestGraphUriFn(path,fName):
    return 'http://example.com%s'%path.split('.')[0]

def ReverseTransform(graph):
    from rdflib import Namespace, RDF
    from amara.writers.struct import structwriter, E, ROOT
    from cStringIO import StringIO
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    V    = Namespace("http://www.w3.org/2006/vcard/ns#")

    src = StringIO()
    w   = structwriter(indent=u"yes", stream=src)
    def attributes(personUri):
        attr = {}
        for _name in graph.query(
            "SELECT ?name [] a foaf:Person; foaf:businessCard [ v:fn ?name ]",
            initNs = { u'foaf' : FOAF, u'v' : V }
        ):
            attr[u'name'] = _name
        return attr
    for person in graph.subjects(RDF.type,FOAF.Person):
        w.feed(ROOT(E(u'Patient',attributes(person))))
    return src.getvalue()

@service(SERVICE_ID, 'diglot')
@grddl_graphstore_resource('/diglot', TestGraphUriFn, caching = True)
def grddl_graphstore_protocol(): pass
import inspect
from webob import Request
from akara import request, response, global_config, registry
from akamu.config.dataset import ConnectToDataset
from rdflib.Graph import ConjunctiveGraph
from rdflib import plugin, URIRef, OWL, RDFS, RDF, Namespace

FOAF_NS    = Namespace('http://xmlns.com/foaf/0.1/')
WEB_ACL_NS = Namespace('http://www.w3.org/ns/auth/acl#')
WORLD      = FOAF_NS.Agent
AKAMU_WEB_ACL_NS = Namespace('https://code.google.com/p/akamu/WebACL#')

EXECUTE_MODE = AKAMU_WEB_ACL_NS.Execute

ACL_WORLD_QUERY=\
"""
PREFIX    acl: <http://www.w3.org/ns/auth/acl#>
PREFIX   foaf: <http://xmlns.com/foaf/0.1/>
ASK {
    []  acl:accessTo    %s;
        acl:mode        %s;
        acl:agentClass  foaf:Agent .
}"""

ACL_CHECK_DIRECTLY_QUERY= \
"""
PREFIX    acl: <http://www.w3.org/ns/auth/acl#>
PREFIX   foaf: <http://xmlns.com/foaf/0.1/>
ASK {
    []  a               ?class;
        foaf:name       "%s" .
    []  acl:accessTo    %s;
        acl:mode        %s;
        acl:agentClass  ?class .
}"""

ACCESS_MAP = {
    "GET"    : WEB_ACL_NS.Read,
    "PUT"    : WEB_ACL_NS.Write,
    "POST"   : EXECUTE_MODE,#WEB_ACL_NS.Append,
    "DELETE" : WEB_ACL_NS.Write,
    "PATCH"  : WEB_ACL_NS.Write,
}

class web_acl(object):
    """
    Decorator of Akara services which is expected to be used with repoze.who middleware
    and manages access to the decorated service using a (configured) AkamuGraphStore
    (specified by the first argument) comprising assertions with terms from the
    WAC vocabulary:

    http://www.w3.org/wiki/WebAccessControl/Vocabulary

    as well as assertions about users:

    []  a .. agent class ..;
        foaf:name "ikenna" .

    The classes associated with the user via rdf:type statements correspond to
    agentClasses used in statements such as:

    []  acl:accessTo    <http://example.com/service/1>;
        acl:agentClass  .. agent class .. .

    Then a service decorated this way

    @simple_service('GET', '<http://example.com/service/1>','service.1','text/plain',wsgi_wrapper=..)
    @web_acl('.. akamu graph store ..','<http://example.com/service/1>')
    def service_2():
        ..snip..

    (where .. akamu graph store .. is a graph store with the assertions above) will control
    access, ensuring that the request has been properly authenticated by repoze.who and
    that the WAC assertions indicate the user has access to the service, returning a 403 or 401
    otherwise, depending on the circumstance.

    RDF statements made using the acl:mode property are currently ignored
    """
    def __init__(self,acl_dataset,accessMap = None,simple_service=True,debug=False):
        self.simple_service         = simple_service
        self.cache                  = {}
        self.acl_dataset            = acl_dataset
        self.accessMap = ACCESS_MAP.copy()
        self.debug                  = debug
        if accessMap:
            self.accessMap.update(accessMap)

    def __call__(self, func):
        def innerHandler(*args, **kwds):
            req = Request(request.environ)
            _path = req.path[1:] if req.path[0] == '/' else req.path
            service_uri = URIRef(
                registry._current_registry._registered_services[_path].ident
            )
            user = request.environ.get('REMOTE_USER')
            if not user:
                if self.simple_service:
                    response.code = 401
                    return "Not authorized to access this resource"
                else:
                    environ, start_response = args
                    start_response("401 Unauthorized",[])
                    return "Not authorized to access this resource"
            else:
                if '_' in kwds:
                    del kwds['_']
            allowed = self.cache.get(user)
            if allowed is None:
                accessMode = self.accessMap.get(req.method)
                if accessMode is None:
                    allowed = False
                    if debug:
                        print "HTTP method not mapped, no access granted!"
                else:
                    cg =  ConjunctiveGraph(
                            ConnectToDataset(self.acl_dataset)
                    )
                    query = ACL_WORLD_QUERY%(service_uri.n3(),accessMode.n3())
                    any_user = cg.query(query).serialize(format='python')
                    if self.debug:
                        print query, any_user

                    query = ACL_CHECK_DIRECTLY_QUERY%(
                        user,
                        service_uri.n3(),
                        accessMode.n3()
                    )
                    allowed_by_group = cg.query(query).serialize(format='python')
                    if self.debug:
                        print query, allowed_by_group
                    allowed = allowed_by_group or any_user
                    self.cache[user] = allowed
            if allowed:
                if self.simple_service:
                    argInfo = inspect.getargspec(func)
                    vargs    = argInfo.varargs
                    keywords = argInfo.keywords

                    if keywords is None and argInfo.defaults:
                        keywords = argInfo.args[-len(argInfo.defaults):]
                        vargs    = argInfo.args[:-len(argInfo.defaults)]
                    if vargs and keywords:
                        return func(*args, **kwds)
                    elif vargs:
                        return func(*args)
                    elif keywords:
                        return func(**kwds)
                    else:
                        return func()
                else:
                    environ, start_response = args
                    return func(environ, start_response)
            else:
                if self.simple_service:
                    response.code = 403
                    return "The authenticated user is forbidden from accessing this resource"
                else:
                    environ, start_response = args
                    start_response("403 Forbidden",[])
                    return "The authenticated user is forbidden from accessing this resource"
        return innerHandler
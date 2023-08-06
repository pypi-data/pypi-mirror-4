import sys
from StringIO import StringIO
from webob import Request
from akamu.security.acl    import web_acl, WEB_ACL_NS
from akamu.security.repoze import RepozeWrapper
from akara.services        import service, simple_service
from rdflib import plugin, URIRef, OWL, RDFS, RDF, Namespace

ACCESS_NS = Namespace('http://example.com/access_classes/')

SERVICE_ID_PREFIX = 'http://example.com/service/'

def CreateRepozeMiddleWare(app):
    from repoze.who.plugins.htpasswd import HTPasswdPlugin
    from repoze.who.plugins.basicauth import BasicAuthPlugin
    from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
    from repoze.who.plugins.redirector import RedirectorPlugin
    from repoze.who.interfaces import IChallenger
    from repoze.who.middleware import PluggableAuthenticationMiddleware
    io = StringIO()
    io.write('admin:admin')
    io.seek(0)
    def cleartext_check(password, hashed):
        return password == hashed
    htpasswd = HTPasswdPlugin(io, cleartext_check)
    basicauth = BasicAuthPlugin('repoze.who')
    redirector = RedirectorPlugin('/login')
    redirector.classifications = {IChallenger:['browser'],} # only for browser
    identifiers = [('basicauth', basicauth)]
    authenticators = [('htpasswd', htpasswd)]
    challengers = [('redirector', redirector),
                   ('basicauth', basicauth)]
    mdproviders = []

    from repoze.who.classifiers import default_request_classifier
    from repoze.who.classifiers import default_challenge_decider
    import logging
    log_stream = sys.stdout

    return PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        default_request_classifier,
        default_challenge_decider,
        log_stream = log_stream,
        log_level = logging.DEBUG
    )


def service_stub(environ, start_response, supported_methods):
    req = Request(environ)
    if req.method not in supported_methods:
        start_response("405 Method Not Allowed", [])
        return "Method not allowed for this resource"
    else:
        rt = 'Success'
        start_response("200 Ok",
                       [("Content-Type", 'text/plain'),
                        ("Content-Length", len(rt))]
        )
        return rt


@service(SERVICE_ID_PREFIX+'1','service.1',wsgi_wrapper=CreateRepozeMiddleWare)
@web_acl('mysqlDataset',simple_service=False)
def service_1(environ, start_response):
    return service_stub(
        environ,
        start_response,
        ['POST','GET']
    )

@service(SERVICE_ID_PREFIX + '2', 'service.2',wsgi_wrapper=CreateRepozeMiddleWare)
@web_acl('mysqlDataset',
         accessMap = { "POST" : WEB_ACL_NS.Append },
         simple_service=False)
def service_2(environ, start_response):
    return service_stub(
                environ,
                start_response,
                ['POST','GET','PUT']
    )

@simple_service(
    'GET' ,
    SERVICE_ID_PREFIX + '3',
    'service.3',
    'text/plain',
    wsgi_wrapper=CreateRepozeMiddleWare)
@web_acl('mysqlDataset')
def service_3(): return "Success"
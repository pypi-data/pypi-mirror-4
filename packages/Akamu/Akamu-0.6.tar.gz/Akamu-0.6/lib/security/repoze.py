from akamu.wheezy import WheezyCachingAdapterSetup
from akara import global_config
from akara import module_config as config

def RepozeWrapper(app):
    """
    Used by the wsgi_wrapper keyword for Akara service decorators to
    use repoze.who as middleware to conditionally places identification
    and authentication information (including a REMOTE_USER value)
    into the WSGI environment for the downstream , decorated Akara service

    It expects a key in the configuration called 'repoze_config' whose
    value is the path to a repoze configuration file:

    http://docs.repoze.org/who/1.0/narr.html#middleware-configuration-via-config-file
    """

    from repoze.who.config import make_middleware_with_config
    return make_middleware_with_config(
        app,
        {'here' : global_config.config_root},
        config().get('repoze_config')
    )

class WheezyRepozeWrapper(object):
    """
    Used by the wsgi_wrapper keyword for Akara service decorators to
    use both repoze.who and Wheezy as middleware.  The arguments it takes
    are the same as akamu.wheezy.WheezyCachingAdapterSetup.

    It expects a memcache_socket in the module's configuration that points
    to the memcache socket to use for cache persistence.

    It also expects a key in the configuration called 'repoze_config' whose
    value is the path to a repoze configuration file:

    http://docs.repoze.org/who/1.0/narr.html#middleware-configuration-via-config-file

    Client <-> ( .... ( Repoze ( WheezyCaching ( Akara service
    """
    def __init__(self,
                 options = None,
                 noCache = False,
                 dependency = None,
                 noauth = False,
                 queries = None,
                 debug = False,
                 ttl=15):
        self.noauth        = noauth
        self.wheezyWrapper = WheezyCachingAdapterSetup(
            options,
            noCache,
            dependency,
            queries,
            debug=debug,
            ttl=ttl,
            memcache_socket=config().get('memcache_socket')
        )
    def __call__(self,akara_app):
        if self.noauth:
            return self.wheezyWrapper(akara_app)
        else:
            from repoze.who.config import make_middleware_with_config
            return make_middleware_with_config(
                self.wheezyWrapper(akara_app),
                {'here' : global_config.config_root},
                config().get('repoze_config')
            )

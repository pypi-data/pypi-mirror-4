__author__ = 'chimezieogbuji'

from wheezy.http.response import HTTPResponse
from wheezy.http.middleware import http_cache_middleware_factory
from wheezy.http.cache import CacheableResponse, NotModifiedResponse
from wheezy.caching import CacheDependency
from wheezy.http import bootstrap_http_defaults, CacheProfile, WSGIApplication
from wheezy.caching import MemoryCache
from wheezy.http import HTTPCachePolicy
from datetime import timedelta
from wheezy.core.collections import defaultdict
from wheezy.core.datetime import parse_http_datetime
from wheezy.http.cacheprofile import RequestVary

#Memory cache (local to akara process)
#cache = MemoryCache()

#memcache (distributed)
from wheezy.caching.memcache import client_factory
cache = client_factory(['unix:/tmp/memcached.sock'])

cache_factory = lambda: cache

class WheezyCachingAdapterSetup(object):
    def __init__(self,
                 options = None,
                 noCache = False,
                 dependency = None,
                 queries = None,
                 environ = None,
                 debug = False,
                 asFn = False,
                 ttl=15):
        """
        Used as an Akara WSGI wrapper, i.e.:
        @simple_service(...,wsgi_wrapper=WheezyCachingAdapterSetup( ... ))

        Produces a wheezy.http.WSGIApplication that takes WheezyAkaraMiddleWareFactory

        If options aren't provided, the default is a
        wheezy.http.middleware.http_cache_middleware_factory and the following options:
         'ENCODING': 'utf-8',
         'http_cache_factory': .. memcache factory (with socket in /tmp/memcached.sock) ..
         )

        noCache indicates whether responses aren't cached (for services that need
        to invalidate a cache but don't cache themselves)

        dependency indicates the name of this cache for reference in another
        service that invalidates it

        queries is a list of query key's that will be used to compose the key for caching
        responses to requests

        Within an Akara service decorated in this way, a wheezy.http.HTTPCachePolicy instance can be created:

            policy = request.environ['wheezy.http.HTTPCachePolicy']('public')

        And then its various methods can be used to control cache-specific HTTP headers
        of the response:
            See: http://packages.python.org/wheezy.http/userguide.html#cache-policy

        Then request.environ['wheezy.http.cache_policy'] needs to be set to the policy:

            request.environ['wheezy.http.cache_policy'] = policy

        As an alternative to providing a static dependency name via the dependency
        keyword argument, it can be provided via:

            request.environ['wheezy.http.cache_dependency'] = '.. cache name ..'

        Cache can be invalidated by (dependency) name via:

            request.environ['akamu.wheezy.invalidate']('..cache name..')

        See:
            - http://packages.python.org/wheezy.http/userguide.html#cache-profile
            - http://packages.python.org/wheezy.caching/userguide.html#cachedependency

        """
        self.ttl        = ttl
        self.asFn       = asFn
        self.debug      = debug
        self.queries    = queries if queries else None
        self.environ    = environ if environ else None
        self.noCache    = noCache
        self.depepdency = dependency
        self._middlewareFactories = [WheezyAkaraMiddleWareFactory]
        self._options = options if options else {
            'ENCODING': 'utf-8',
            'http_cache_factory': cache_factory
        }
        if dependency:
            self._options['dependency'] = dependency
        if noCache:
            self._options['noCache']    = True
        if self.queries:
            self._options['queries']    = self.queries
        if self.environ:
            self._options['environ']    = self.environ
        self._options['debug']          = self.debug
        self._options['ttl']            = self.ttl

    def __call__(self,akara_application):
        self._options['akara_application']     = akara_application
        if self.asFn:
            self.wsgiFN = WSGIApplication(self._middlewareFactories,options=self._options)
            def fn(environ, start_response):
                return self.wsgiFN(environ,start_response)
            return fn
        else:
            return WSGIApplication(self._middlewareFactories,options=self._options)

global_profiles = defaultdict(lambda: None)

class WheezyAkaraMiddleWareFactory(object):
    """
    Wheezy WSGI middleware (http://packages.python.org/wheezy.http/userguide.html#middleware)
    that corresponds to the following combination:

        wheezy.http.middleware.http_cache_middleware_factory,
        wheezy.http.middleware.environ_cache_adapter_middleware_factory,
        wheezy.http.middleware.wsgi_adapter_middleware_factory

    Where wsgi_adapter_middleware_factory wraps an Akara application, is extended
    to provide wheezy.caching capabilities to the akara handler via request.environ, and
    uses a memcache factory connected to a running socket in /tmp/memcached.sock

    See: http://packages.python.org/wheezy.caching/userguide.html#python-memcached

    """
    def __init__(self,options):
        self.debug             = options['debug']
        self.akara_application = options['akara_application']
        self.options           = options

        middleware_vary = options.get('http_cache_middleware_vary', None)
        if middleware_vary is None:
            middleware_vary = RequestVary(
                query   = self.options['queries'] if 'queries' in self.options
                    else None,
                environ = self.options['environ'] if 'environ' in self.options
                else None)
            options['http_cache_middleware_vary'] = middleware_vary

        self.middleware_vary = middleware_vary
        self.profiles = global_profiles

    def __call__(self, request, following):
        """
        Combination of (in order):
            - wsgi_adapter_middleware_factory (with akara application)
            - environ_cache_adapter_middleware_factory
        """
        def InvalidateCacheViaDependency(cacheName):
            if self.debug:
                print "invalidating cache: ", cacheName
            dependency = CacheDependency(cacheName)
            dependency.delete(cache_factory())

        assert not following
        request.environ['wheezy.http.HTTPCachePolicy'] = HTTPCachePolicy
        request.environ['akamu.wheezy.invalidate']     = InvalidateCacheViaDependency

        response = HTTPResponse()

        def start_response(status, headers):
            response.status_code = int(status.split(' ', 1)[0])
            response.headers = [(name, value) for name, value in headers
                                              if name != 'Content-Length']
            return response.write_bytes
        result = self.akara_application(request.environ, start_response)
        try:
            response.buffer.extend(result)
        finally:
            if hasattr(result, 'close'):  # pragma: nocover
                result.close()

        from amara.xslt.result import stringresult
        def normalizeResult(item):
            if isinstance(item,stringresult):
                return unicode(item)#._stream.getvalue()
            else:
                return item

        response.buffer = map(normalizeResult,response.buffer)
        environ = request.environ
        policy = None
        if 'wheezy.http.cache_policy' in environ:
            policy = environ['wheezy.http.cache_policy']
            response.cache_policy = policy

        if 'noCache' in self.options:
            response.cache_profile = CacheProfile('none', no_store=True)
        else:
            response.cache_profile = CacheProfile('public', duration=timedelta(minutes=self.options['ttl']))

        assert (policy or
                'wheezy.http.noCache' in environ or
                'noCache' in self.options or
                response.status_code != 200)
        dependency = self.options.get(
            'dependency',
            environ.get('wheezy.http.cache_dependency'))
        if self.debug:
            print "Cache name: (for dependencies) %s"%dependency if dependency else "No cache name given!"
        if dependency:
            response.dependency = CacheDependency(dependency)

        _response = response

        middleware_key = 'C' + self.middleware_vary.key(request)
        _cache_profile = self.profiles[middleware_key]
        if _cache_profile:
            request_key = _cache_profile.request_vary.key(request)
            context = cache_factory()
            cache = context.__enter__()
            try:
                response = cache.get(request_key, _cache_profile.namespace)
            finally:
                context.__exit__(None, None, None)
            if response and _response.status_code == 200:  # cache hit
                if self.debug:
                    print "Cache hit!", request_key
                environ = request.environ
                if response.etag:
                    none_match = environ.get('HTTP_IF_NONE_MATCH', None)
                    if none_match and response.etag in none_match:
                        return NotModifiedResponse(response)
                if response.last_modified:
                    modified_since = environ.get(
                        'HTTP_IF_MODIFIED_SINCE', None)
                    if modified_since:
                        modified_since = parse_http_datetime(modified_since)
                        if modified_since >= response.last_modified:
                            return NotModifiedResponse(response)
                return response
            else:
                response = _response
                if self.debug:
                    print "No cache hit"
        if response.status_code == 200:
            response_cache_profile = response.cache_profile
            if 'noCache' not in self.options and response_cache_profile:
                if _cache_profile != response_cache_profile:
                    self.profiles[middleware_key] = response_cache_profile
                    request_key = response_cache_profile.request_vary.key(
                        request)
                dependency = response.dependency
                response = CacheableResponse(response)
                context = cache_factory()
                cache = context.__enter__()
                try:
                    if dependency:
                        if self.debug:
                            print "Attempting to set cache (with dependency)"
                        cache.set_multi({
                            request_key: response,
                            dependency.next_key(
                                cache,
                                response_cache_profile.namespace
                            ): request_key},
                            response_cache_profile.duration,
                            '',
                            response_cache_profile.namespace)
                    else:
                        if self.debug:
                            print "Attempting to set cache (without dependency)"
                        cache.set(
                            request_key,
                            response,
                            response_cache_profile.duration,
                            response_cache_profile.namespace)
                finally:
                    context.__exit__(None, None, None)
        return response

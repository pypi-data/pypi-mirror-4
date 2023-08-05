__author__ = 'chimezieogbuji'

import cgi, amara
from akara.services import simple_service
from cStringIO import StringIO
from amara.writers.struct import structwriter, E, NS, ROOT
from amara.lib import U
from akara import request
from akamu.wheezy import WheezyCachingAdapterSetup
from akara import request, response

XHTML_IMT  = 'application/xhtml+xml'
XML_IMT    = 'application/xml'
HTML_IMT   = 'text/html'
XHTML_NS   = u'http://www.w3.org/1999/xhtml'
SERVICE_ID = 'http://example.com/wheezy'

@simple_service('GET',
                SERVICE_ID,
                'wheezy.test',
                XHTML_IMT,
                wsgi_wrapper=WheezyCachingAdapterSetup(dependency='xhtmlContent'))
def wheezy_service():
    policy = request.environ['wheezy.http.HTTPCachePolicy']('public')

    policy.etag('12345')
    request.environ['wheezy.http.cache_policy']  = policy
    src    = StringIO()
    w = structwriter(indent=u"yes", stream=src)
    w.feed(
        ROOT(
            E((XHTML_NS,u'html'),
                E((XHTML_NS,u'body'),
                    E((XHTML_NS,u'p'),u'Testing')
                )
            )
        )
    )
    return src.getvalue()

@simple_service('GET',
                SERVICE_ID,
                'wheezy.test.clear_cache',
                XHTML_IMT,
                wsgi_wrapper=WheezyCachingAdapterSetup(noCache=True))
def wheezy_service2():
    request.environ['akamu.wheezy.invalidate']('xhtmlContent')
    return "Nothing"
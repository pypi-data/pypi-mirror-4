__author__ = 'chimezieogbuji'

import cgi, inspect, re
from cStringIO   import StringIO
from amara.xslt  import transform
from akara       import request, response, global_config
from Ft.Xml.Xslt import Processor
from Ft.Xml      import InputSource
from Ft.Lib      import Uri

from akamu.xslt.extensions import NS

FIREFOX_PATTERN = re.compile(r'15\..+')
IE_9_PATTERN    = re.compile(r'9.0.+')
IE_8_PATTERN    = re.compile(r'8.0.+')
OPERA_PATTERN   = re.compile(r'11.62.+')
SAFARI_PATTERN  = re.compile(r'5.1.3')
CHROME_PATTERN  = re.compile(r'20\..*')

#See: http://greenbytes.de/tech/tc/xslt/
CLIENT_SIDE_BROWSERS = [
    ('Firefox',FIREFOX_PATTERN),
    ('Microsoft Internet Explorer', IE_9_PATTERN),
    ('Microsoft Internet Explorer',IE_8_PATTERN),
    ('Opera',OPERA_PATTERN),
    ('Safari',SAFARI_PATTERN),
    ('Chrome',CHROME_PATTERN),
]

def ClientSideXSLTCapable(environ):
    import httpagentparser
    agentInfo = httpagentparser.detect(environ.get('HTTP_USER_AGENT', ''))
    browserInfo = agentInfo['browser']
    supported = filter(lambda (name,versionPattn):
                            browserInfo['name'] == name and
                            versionPattn.match(browserInfo['version']),
                       CLIENT_SIDE_BROWSERS)
    return bool(supported)

def TransformWithAkamuExtensions(src,xform,manager,params=None,baseUri=NS):
    params = params if params else {}
    processor         = Processor.Processor()
    processor.manager = manager
    processor.registerExtensionModules(['akamu.xslt.extensions'])

    result = StringIO()
    source = InputSource.DefaultFactory.fromString(src,baseUri)
    isrc   = InputSource.DefaultFactory.fromString(xform,baseUri)
    processor.appendStylesheet(isrc)
    processor.run(
        source,
        outputStream=result,
        ignorePis=True,
        topLevelParams=params
    )
    return result.getvalue()

NOOPXML = u'<Root/>'

class xslt_rest(object):
    """
    Decorator of Akara services that will cause all invokations to
    route HTTP (query or form) parameters into the transform as
    xslt parameters.  The source of the transform (a string) is given by applying
    a user-specified function against the parameters and
    the result of the transformation of this (using a user-specified
    transform) is used as the result of the service
    """
    def __init__(self, transform, source = None, argRemap = None, parameters = None, clientSide = False):
        self.clientSide = clientSide
        self.argRemap  = argRemap if argRemap else {}
        self.transform = transform
        self.params    = parameters if parameters else {}
        self.source = source if source else None

    def __call__(self, func):
        def innerHandler(*args, **kwds):
            argNames = inspect.getargspec(func).args
            parameters = self.params
            isaPost = len(args) == 2 and list(argNames) == ['body','ctype']
            if isaPost:
                #Parameters in POST body
                fields = cgi.FieldStorage(
                    fp=StringIO(args[0]),
                    environ=request.environ
                )
                for k in fields:
                    val = fields.getvalue(k)
                    if k in self.argRemap:
                        parameters[self.argRemap[k]] = val
                    else:
                        parameters[k] = val
            else:
                #parameters to service method are GET query arguments
                for idx,argName in enumerate(argNames):
                    if argName in self.argRemap:
                        parameters[self.argRemap[argName]] = args[idx] if len(args) > idx + 1 else kwds[argName]
                    elif len(args) > idx + 1 or argName in kwds:
                        parameters[argName] = args[idx] if len(args) > idx + 1 else kwds[argName]
                for k,v in kwds.items():
                    if k in self.argRemap:
                        parameters[self.argRemap[k]] = v
                    else:
                        parameters[k] = v

            #Route non-keyword and keyword arguments and their values to
            #XSLT parameters
            argInfo = inspect.getargspec(func)
            vargs    = argInfo.varargs
            keywords = argInfo.keywords
            if keywords is None and argInfo.defaults:
                keywords = argInfo.args[-len(argInfo.defaults):]
                vargs    = argInfo.args[:-len(argInfo.defaults)]
            if isaPost:
                src = func(*args) if not self.source else self.source
            elif vargs and keywords:
                src = func(*args, **kwds) if not self.source else self.source
            elif vargs:
                src = func(*args) if not self.source else self.source
            elif keywords:
                src = func(**kwds) if not self.source else self.source
            else:
                src = func() if not self.source else self.source
            isInfoResource = (isinstance(response.code,int) and
                              response.code == 200
                             ) or (isinstance(response.code,basestring) and
                                   response.code.lower()) == '200 ok'
            if not isInfoResource:
                #If response is not a 200 then we just return it (since we can't
                # be invoking an XSLT HTTP operation)
                return src
            else:
                if isinstance(src,tuple) and len(src)==2:
                    src,newParams = src
                    parameters.update(newParams)
                authenticatedUser = request.environ.get('REMOTE_USER')
                if authenticatedUser:
                    parameters[u'user'] = authenticatedUser
                elif u'user' in parameters:
                    del parameters[u'user']
                if self.clientSide:
                    from amara.bindery import parse
                    doc = parse(src)
                    pi = doc.xml_processing_instruction_factory(
                        u"xml-stylesheet",
                        u'href="%s" type="text/xsl"'%self.transform)
                    doc.xml_insert(0,pi)
                    return doc
                else:
                    return transform(src,self.transform,params=parameters)
        return innerHandler
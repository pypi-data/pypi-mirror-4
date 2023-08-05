__author__ = 'chimezieogbuji'

from cStringIO                 import StringIO
from Ft.Xml.Xslt               import XsltElement, ContentInfo, AttributeInfo
from Ft.Xml.XPath              import Conversions
from Ft.Xml.Domlette           import NonvalidatingReader
from Ft.Xml.Xslt               import OutputParameters
from Ft.Xml.Xslt.CopyOfElement import CopyNode
from akamu.config.dataset      import ConnectToDataset
from rdflib.Graph              import Graph, ConjunctiveGraph
from rdflib                    import plugin, URIRef

NS=u'tag:metacognitionllc.com,2012:AkamuXsltExtensions'

class SPARQLQueryElement(XsltElement):
    """
    This extension evaluates a SPARQL query either against the Akamu RDF data
    set(s) identified by name either within the targetGraph or across the entire
    dataset.  The schema is a path within the Akamu Diglot FS to an OWL or RDFS
    documentation of the vocabulary for use in optimizing queries over
    MySQL/layercake-python datasets

    The body of this element is a template; when the template is instantiated,
    it is processed as a SPARQL query string evaluated using the given
    extension attributes

    """
    content = ContentInfo.Template
    legalAttrs = {
        'targetGraph'      : AttributeInfo.StringAvt(default=''),
        'datasetName'      : AttributeInfo.StringAvt(default=''),
        'schema'           : AttributeInfo.StringAvt(default='')
    }

    def instantiate(self, context, processor):
        try:
            # Set the output to an RTF writer, which will create an RTF for
            # us.
            processor.pushResultTree(self.baseUri)

            # The template is manifested as children of the extension element
            # node.  Instantiate each in turn.
            for child in self.children:
                child.instantiate(context, processor)
        # You want to be sure you re-balance the stack even in case of
        # error.
        finally:
            # Retrieve the resulting RTF.
            result_rtf = processor.popResult()
            query=result_rtf.childNodes[0].nodeValue
            context.setProcessState(self)
            context.processorNss = self.namespaces
            targetGraph     = Conversions.StringValue(self._targetGraph.evaluate(context))
            datasetName     = Conversions.StringValue(self._datasetName.evaluate(context))
            schema          = self._schema.evaluate(context)

            store   = ConnectToDataset(datasetName)

            dataset = Graph(store,URIRef(targetGraph)) if targetGraph else ConjunctiveGraph(store)

            print "SPARQL: \n%s" % query
            if schema:
                pass
#                ontGraph=Graph().parse(StringIO(repo.fetchResource(schema).getContent()))
#                for litProp,resProp in ontGraph.query(OWL_PROPERTIES_QUERY,
#                    initNs={u'owl':OWL_NS}):
#                    if litProp:
#                        print "\t Registering literal property ", litProp
#                        dataset.store.literal_properties.add(litProp)
#                    if resProp:
#                        print "\t Registering resource property ", resProp
#                        dataset.store.resource_properties.add(resProp)
            try:
                rt  = dataset.query(
                            query.encode('utf-8'),
                            initNs=self.namespaces).serialize(format='xml')
                doc = NonvalidatingReader.parseString(
                        rt.encode('utf-8'),
                        'tag:ogbujic@ccf.org:2007:meaninglessURI')
#    doc = _dispatchSPARQLQuery(connection,
#                    storeKind,
#                    storeIdentifier,
#                    dataset,
#                    targetGraph,
#                    query,
#                    self.namespaces)
            except:
                #Error
                import traceback
                st = StringIO()
                traceback.print_exc(file=st)
                processor.xslMessage(st.getvalue())
                raise
            processor.writers[-1].copyNodes(doc.documentElement)

class CreateResourceElement(XsltElement):
    content = ContentInfo.Template
    legalAttrs = {
        'path'      : AttributeInfo.StringAvt(default=''),
        'literal-content' : AttributeInfo.YesNo(
            default='no',
            description=('If yes, treat the content literally, i.e. do not'
                         ' execute any XSLT instructions or extensions')),
        'method' : AttributeInfo.QNameAvt(),
        'version' : AttributeInfo.NMTokenAvt(),
        'encoding' : AttributeInfo.StringAvt(),
        'omit-xml-declaration' : AttributeInfo.YesNoAvt(),
        'standalone' : AttributeInfo.YesNoAvt(),
        'doctype-public' : AttributeInfo.StringAvt(),
        'doctype-system' : AttributeInfo.StringAvt(),
        'cdata-section-elements' : AttributeInfo.QNamesAvt(),
        'indent' : AttributeInfo.YesNoAvt(),
        'media-type' : AttributeInfo.StringAvt(),
    }

    doesSetup = True
    def setup(self):
        self._output_parameters = OutputParameters.OutputParameters()
        return

    def instantiate(self, context, processor):
        context.setProcessState(self)
        stream = StringIO()
        self._output_parameters.avtParse(self, context)
        processor.addHandler(self._output_parameters, stream)
        literal_content = self._literal_content
        if literal_content:
            for child in self.children:
                CopyNode(processor, child)
        else:
            self.processChildren(context, processor)
        processor.removeHandler()
        text = stream.getvalue()
        path = Conversions.StringValue(self._path.evaluate(context))
        processor.manager.createResource(path,text.encode('utf-8'))

class GetResourceContentElement(XsltElement):
    content = ContentInfo.Empty
    legalAttrs = {
        'path'      : AttributeInfo.StringAvt(default='')
    }
    def instantiate(self, context, processor):
        context.setProcessState(self)
        path = Conversions.StringValue(self._path.evaluate(context))
        content = processor.manager.getResource(path).getContent()
        doc = NonvalidatingReader.parseString(content,NS)
        processor.writers[-1].copyNodes(doc.documentElement)

def GetResourceFunction(context,path):
    content = context.processor.manager.getResource(path).getContent()
    doc = NonvalidatingReader.parseString(content,NS)
    return [ doc.documentElement ]

class UpdateResourceElement(XsltElement):
    legalAttrs = {
        'path'      : AttributeInfo.StringAvt(default=''),
        'literal-content' : AttributeInfo.YesNo(
            default='no',
            description=('If yes, treat the content literally, i.e. do not'
                         ' execute any XSLT instructions or extensions')),
        'method' : AttributeInfo.QNameAvt(),
        'version' : AttributeInfo.NMTokenAvt(),
        'encoding' : AttributeInfo.StringAvt(),
        'omit-xml-declaration' : AttributeInfo.YesNoAvt(),
        'standalone' : AttributeInfo.YesNoAvt(),
        'doctype-public' : AttributeInfo.StringAvt(),
        'doctype-system' : AttributeInfo.StringAvt(),
        'cdata-section-elements' : AttributeInfo.QNamesAvt(),
        'indent' : AttributeInfo.YesNoAvt(),
        'media-type' : AttributeInfo.StringAvt(),
        }

    doesSetup = True
    def setup(self):
        self._output_parameters = OutputParameters.OutputParameters()
        return

    def instantiate(self, context, processor):
        context.setProcessState(self)
        stream = StringIO()
        self._output_parameters.avtParse(self, context)
        processor.addHandler(self._output_parameters, stream)
        literal_content = self._literal_content
        if literal_content:
            for child in self.children:
                CopyNode(processor, child)
        else:
            self.processChildren(context, processor)
        processor.removeHandler()
        text = stream.getvalue()
        path = Conversions.StringValue(self._path.evaluate(context))
        res = processor.manager.getResource(path)
        res.update(text)

ExtFunctions = {
#    (NS, 'sparql-query') : SPARQLQueryFunction,
    (NS, 'get-resource') : GetResourceFunction
}

ExtElements = {
    (NS, 'sparql-query')    : SPARQLQueryElement,
    (NS, 'create-resource') : CreateResourceElement,
    (NS, 'get-resource')    : GetResourceContentElement,
    (NS, 'update-resource') : UpdateResourceElement
}
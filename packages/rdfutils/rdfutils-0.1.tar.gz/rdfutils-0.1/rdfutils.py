# Copyright 2006-2012 the Active Archives contributors (see AUTHORS)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Thin wrapper functions to work with an RDF store based on the Redland C library
& Python bindings (librdf, python-librdf (python module name: RDF))

Requires: RDF
"""


import RDF
from urlparse import urlparse
import os.path


def create_dummy_model ():
    """
    Creates and returns an in-memory HashStorage RDF Model.

    It is useful for testing purpose.
    """
    options = "new='yes', hash-type='memory', contexts='yes'"
    storage = RDF.HashStorage('dummy', options=options)
    return RDF.Model(storage)


def get_model (storage_name, storage_dir):
    """
    Opens/creates and return the default RDF Store (RDF.Model in bdb hashes
    format, contexts enabled).
        
        >>> print(get_model('mydb', '/tmp/'))
        <?xml version="1.0" encoding="utf-8"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        </rdf:RDF>
        <BLANKLINE>
    """
    options = "hash-type='bdb', contexts='yes', dir='%s'" % storage_dir
    storage = RDF.HashStorage(storage_name, options=options)
    return RDF.Model(storage)


def get_postgresql_model (): 
    try:
        storage = RDF.Storage(storage_name='postgresql', name='foo', options_string="contexts='yes', host='localhost', database='foo', user='foo', password='bar'")
    except RedlandError:
        storage = RDF.Storage(storage_name='postgresql', name='foo', options_string="contexts='yes', new='yes', host='localhost', database='foo', user='foo', password='bar'")
    return RDF.Model(storage)


def get_or_create_model (path): 
    """
    Opens/creates and return the default RDF Store (RDF.Model with sqlite
    backend contexts enabled).
        
        >>> print(get_or_create_model('/tmp/foo.db'))
        <?xml version="1.0" encoding="utf-8"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        </rdf:RDF>
        <BLANKLINE>
    """
    if  os.path.exists(path):
        options_string = "contexts='yes'"
    else:
        options_string = "new='yes', contexts='yes'"
    storage = RDF.Storage(storage_name='sqlite', name=path, options_string=options_string)
    return RDF.Model(storage)


def group_by (results, group_by_var, collect_var):
    """
    Reorganizes a SPARQL query result object to gather repeating values as a list of dictionaries.
    Returns a list of dictionaries d, in result order, such that d[collect_var] = [value, value, ...]
    NB: other keys in d only reflect the values of the first result/row with the new group_by_var value.
    """
    ret = []
    last = None
    accum = None
    for r in results:
        cur = r.get(group_by_var)
        if cur != last:
            last = cur
            accum = []
            item = {}
            for key in r.keys():
                if key != collect_var:
                    item[key] = r.get(key)
            item[collect_var] = accum
            ret.append(item)
        accum.append(r.get(collect_var))
    return ret


def rdfnode (node):
    """
    Unpeels an RDF.Node object to a displayable string
    """
    if node == None:
        return ""
    ret = node
    if type(node) == str or type(node) == unicode:
        return node
    if node.is_resource():
        ret = str(node.uri)
    elif node.is_literal():
        ret = unicode(node.literal_value.get("string")).encode('utf-8')
    return ret


def query (query, model, language="sparql"):
    """
    Performs a query against a model, in the given language.

    It basically just ensures that the query is encoded bytes as RDF.Query
    can't deal with unicode.

        >>> model = create_dummy_model()
        >>> q = '''
        ... PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        ... SELECT *
        ... WHERE {
        ...     ?a ?b ?c .
        ... }'''
        >>> print(query(q, model))
        <?xml version="1.0" encoding="utf-8"?>
        <sparql xmlns="http://www.w3.org/2005/sparql-results#">
          <head>
            <variable name="a"/>
            <variable name="b"/>
            <variable name="c"/>
          </head>
          <results>
          </results>
        </sparql>
        <BLANKLINE>
    """
    if (type(query) == unicode):
        query = query.encode("utf-8")
    return RDF.Query(query, query_language=language).execute(model)


class BindingsIterator:
    """
    Convenience iterator for RDF.Query results as lists of bindings (not dictionaries)
    """
    def __init__(self, results):
        self.results = results
        self.bindings = []
        for i in range(results.get_bindings_count()):
            self.bindings.append(results.get_binding_name(i))
    def __iter__(self):
        return self
    def next(self):
        next = self.results.next()
        r = []
        for name in self.bindings:
            r.append(next.get(name))
        return r


def prep_uri (uri):
    """
    Turns a uri string (including raw file paths) into an RDF.Uri object.

        >>> print(prep_uri('bla'))
        file://bla
        >>> print(prep_uri('http:bla'))
        http:///bla
        >>> print(prep_uri('http://stdin.fr'))
        http://stdin.fr
        >>> print(prep_uri('file:bla'))
        file:///bla
    """
    if (type(uri) == unicode):
        uri = uri.encode("utf-8")

    url_parts = urlparse(uri)

    if not url_parts.scheme:
        return RDF.Uri('file://%s' % url_parts.geturl())
    else:
        return RDF.Uri(url_parts.geturl())

    return RDF.Uri(url_parts.geturl())


def rdf_parse_into_model (model, uri, format=None, baseuri=None, context=None):
    """
    Parse the given URI into the default store.
    Format, baseuri, and context are all optional.
    (Default context is uri itself)
    Format = "rdfa", "rdfxml (default)", ... (other values supported by RDF)

        >>> import os.path
        >>> model = create_dummy_model()
        >>> fixtures = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures.xml')
        >>> rdf_parse_into_model(model, fixtures)
        >>> q = '''
        ... PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        ... PREFIX dc: <http://purl.org/dc/elements/1.1/>
        ... SELECT *
        ... WHERE {
        ...     ?resource dc:language "en" .
        ... }'''
        >>> print(query(q, model))
        <?xml version="1.0" encoding="utf-8"?>
        <sparql xmlns="http://www.w3.org/2005/sparql-results#">
          <head>
            <variable name="resource"/>
          </head>
          <results>
            <result>
              <binding name="resource"><uri>http://video.constantvzw.org/vj12/Michael_Moss.ogv</uri></binding>
            </result>
            <result>
              <binding name="resource"><uri>http://video.constantvzw.org/vj12/Goffey-Fuller.ogv</uri></binding>
            </result>
          </results>
        </sparql>
        <BLANKLINE>
    """
    uri = prep_uri(uri)

    if format:
        parser=RDF.Parser(format)
    else:
        parser=RDF.Parser()

    if baseuri != None:
        baseuri = prep_uri(baseuri)
    else:
        baseuri = uri

    if context != None:
        context = RDF.Node(prep_uri(context))
    else:
        context = RDF.Node(uri)

    stream = parser.parse_as_stream(uri, baseuri)
    model.context_remove_statements(context=context)
    model.add_statements(stream, context=context)


def rdf_context_remove_statements (model, context):
    """
    Remove all statements related to context in the default store

    See <http://librdf.org/notes/contexts.html> for an explanation of what a Context is.

        >>> import os.path
        >>> model = create_dummy_model()
        >>> fixtures = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures.xml')
        >>> rdf_parse_into_model(model, fixtures)
        >>> q = '''
        ... PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        ... PREFIX dc: <http://purl.org/dc/elements/1.1/>
        ... SELECT *
        ... WHERE {
        ...     ?resource dc:language "en" .
        ... }'''
        >>> print(query(q, model))
        <?xml version="1.0" encoding="utf-8"?>
        <sparql xmlns="http://www.w3.org/2005/sparql-results#">
          <head>
            <variable name="resource"/>
          </head>
          <results>
            <result>
              <binding name="resource"><uri>http://video.constantvzw.org/vj12/Michael_Moss.ogv</uri></binding>
            </result>
            <result>
              <binding name="resource"><uri>http://video.constantvzw.org/vj12/Goffey-Fuller.ogv</uri></binding>
            </result>
          </results>
        </sparql>
        <BLANKLINE>
         
        >>> rdf_context_remove_statements(model,fixtures)
         
        >>> print(query(q, model))
        <?xml version="1.0" encoding="utf-8"?>
        <sparql xmlns="http://www.w3.org/2005/sparql-results#">
          <head>
            <variable name="resource"/>
          </head>
          <results>
          </results>
        </sparql>
        <BLANKLINE>
    """
    context = RDF.Node(prep_uri(context))
    model.context_remove_statements(context=context)


class SparqlQuery (object):
    """
    Thin SPARQL query builder, text only (not RDF specific)

    Example of use:

        >>> import os.path
        >>> model = create_dummy_model()
        >>> fixtures = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures.xml')
        >>> rdf_parse_into_model(model, fixtures)

        >>> q = SparqlQuery()
        >>> q.prefix("dc:<http://purl.org/dc/elements/1.1/>")
        >>> q.prefix("dc:<http://purl.org/dc/elements/1.1/>")
        >>> q.select("*")
        >>> q.where("?resource dc:language 'en'.")
        >>> q.where("?resource dc:format 'video/ogg'.")
        >>> #q.order_by("?label ?value")
        >>> print(q.render())
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dc:<http://purl.org/dc/elements/1.1/>
        SELECT *
        WHERE {
          ?resource dc:language 'en'.
          ?resource dc:format 'video/ogg'.
        }
        <BLANKLINE>
        >>> # to actually perform the query using RDF:
        >>> #rdfquery = RDF.Query(querytext.encode("utf-8"), query_language="sparql")
        >>> #results = rdfquery.execute(rdfmodel)
    """
    def __init__(self):
        self._prefixes = ["rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>"]
        self._select = None
        self._wheres = []
        self._whereclauses = None
        self._order_by = None
        self._filters = []
        
    def prefix (self, val):
        if not val in self._prefixes:
            self._prefixes.append(val)

    def select (self, vals, distinct=False):
        self._select = vals
        self._selectdistinct = distinct
        
    def where (self, val):
        val = "  " + val
        self._wheres.append(val)

    def filter (self, val):
        self._filters.append(val)
        
    def order_by(self, val):
        self._order_by = val

    def where_clause(self, clause):
        if self._whereclauses == None:
            self._whereclauses = []
        clause = "    {%s}\n" % clause
        self._whereclauses.append(clause)

    def where_clause_end(self):
        self.where("{\n" + "    UNION\n".join(self._whereclauses) + "  }")
        self._whereclauses = None

    def render(self):
        ret = ""
        ret += "".join(["PREFIX %s\n" % x for x in self._prefixes])
        if self._select:
            if self._selectdistinct:
                ret += "SELECT DISTINCT %s\n" % self._select
            else:
                ret += "SELECT %s\n" % self._select
        if self._wheres:
            ret += "WHERE {\n"
            ret += "".join(["%s\n" % x for x in self._wheres])
            if self._filters:
                ret += "".join(["  FILTER %s\n" % x for x in self._filters])
            ret += "}\n"
        if self._order_by:
            ret += "ORDER BY %s\n" % self._order_by
        
        return ret


def load_links (model, node, literal=False):
    """
    load all the relationship of a uri via the rdf model using SPARQL.

        >>> import os.path
        >>> model = create_dummy_model()
        >>> fixtures = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures.xml')
        >>> rdf_parse_into_model(model, fixtures)
        >>> #load_links(model, 'http://video.constantvzw.org/vj12/Michael_Moss.ogv')
        >>> #load_links(model, 'en', literal=True)
    """
    links_in = []
    links_out = []
    node_stats = []
    as_rel = None

    if literal:
        s = '"%s"' % node
    else:
        s = "<%s>" % node

    q = """
        SELECT DISTINCT ?relation ?object 
        WHERE {{ %s ?relation ?object . }} 
        ORDER BY ?relation
        """ % s

    for b in query(q, model):
        #FIXME: the name context is misleading here as it relates to "RDF Context"
               #everywhere else in this file

        #relation_is_resource = b['relation'].is_resource()
        #relation_uri = rdfnode(b['relation'])

        #if relation_is_resource and relation_uri == "http://purl.org/dc/elements/1.1/title":
            #context['title'] = rdfnode(b['object'])

        #elif relation_is_resource and relation_uri == "http://purl.org/dc/elements/1.1/description":
            #context['description'] = rdfnode(b['object'])

        #elif relation_is_resource and relation_uri == "http://xmlns.com/foaf/0.1/thumbnail":
            #context['thumbnail'] = rdfnode(b['object'])

        #elif b['object'].is_resource():
        if b['object'].is_resource():
            links_out.append(b)

        else:
            node_stats.append(b)

    q = """
        SELECT DISTINCT ?subject ?relation 
        WHERE {{ ?subject ?relation %s . }} 
        ORDER BY ?relation
        """ % s

    for b in query(q, model):
        links_in.append(b)

    if not literal:
        q = """
            SELECT DISTINCT ?subject ?object 
            WHERE {{ ?subject %s ?object . }} 
            ORDER BY ?subject
            """ % s

        as_rel = [x for x in query(q, model)]

    else:
        as_rel = ()

    return dict(node_stats=node_stats, links_out=links_out, links_in=links_in, as_rel=as_rel)


def subject_exists(url):
    """
    Checks weither a url exists a subject in the store.
    """
    # variable bindings format = result of a SELECT query
    # for an ASK query, you probably want librdf_query_results_get_boolean()
    # and librdf_query_results_is_boolean() to check the result type

    q = "ASK { <%s> ?b ?c }" % url
    return query(q, RDF_MODEL).get_boolean()


if __name__ == "__main__":
    import doctest
    doctest.testmod()

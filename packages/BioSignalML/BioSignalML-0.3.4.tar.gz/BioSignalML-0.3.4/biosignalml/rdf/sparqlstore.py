######################################################
#
#  BioSignalML Management in Python
#
#  Copyright (c) 2010-2013  David Brooks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
######################################################

import urllib
import json
import logging

import tornado.ioloop
import tornado.httpclient

import biosignalml.rdf as rdf


def get_result_value(result, column):
#====================================
  """
  Use a type information returned from a SPARQL query to cast a variable's
  value to an appropriate Python class.

  :param result (dict): A dictionary containing a result row as converted
    from a JSON formatted result set.
  :param column (str): The name of a variable in the result set.
  :return: The `value` field, cast according to the `type` and `datatype` fields.
  """
  from biosignalml.utils import isoduration_to_seconds
  NONE = { 'value': '', 'type': 'literal', 'datatype': '' }
  r = result.get(column, NONE)
  rtype = r['type']
  value = r['value']
  if   rtype == 'uri':
    return rdf.Uri(value)
  elif rtype == 'bnode':
    return rdf.BlankNode(value)
  elif rtype == 'typed-literal':
    dt = r['datatype']
    if dt == 'http://www.w3.org/2001/XMLSchema#dayTimeDuration':
      return isoduration_to_seconds(value)
    elif dt == 'http://www.w3.org/2001/XMLSchema#integer':
      return int(value)
    ## Extend...
  return value


class StoreException(Exception):
#===============================
  pass

class SparqlStore(object):
#=========================
  """
  A SPARQL endpoint to a RDF store.

  :param href: The URL of the store.
  :param endpoints: A list with the relative paths to Query,
                    Update, and Graph endpoints.
  """

  ENDPOINTS = [ '/sparql/', '/update/', '/data/' ] #: Order is QUERY, UPDATE, GRAPH

  def __init__(self, href):
  #------------------------
    self._href = href

  def _request(self, endpoint, method, **kwds):
  #--------------------------------------------
    ioloop = tornado.ioloop.IOLoop()
    client = tornado.httpclient.AsyncHTTPClient(ioloop)
    endpoint = self._href + endpoint
    self._response = None
    def callback(response):
      self._response = response
      ioloop.stop()
    client.fetch(endpoint, callback,
                 method=method, connect_timeout=20, **kwds)
    ioloop.start()
    response = self._response
    client.close()
    if response.code == 599:
      print response.body
      raise StoreException("Cannot connect to SPARQL endpoint %s -- is it active?" % endpoint)
    elif response.code not in [200, 201]:
      raise Exception(response.body)
    return response.body

  @staticmethod
  def map_prefixes(prefixes):
  #--------------------------
    return '\n'.join(['PREFIX %s: <%s>' % kv for kv in prefixes.iteritems()] + ['']) if prefixes else ''


  def query(self, sparql, format=rdf.Format.RDFXML, prefixes=None):
  #----------------------------------------------------------------
    """
    Perform a SPARQL query.
    """
    #logging.debug('SPARQL %s: %s', format, sparql)
    try:
      return self._request(self.ENDPOINTS[0], 'POST',
                           body=urllib.urlencode({'query': self.map_prefixes(prefixes) + sparql}),
                           headers={'Content-type': 'application/x-www-form-urlencoded',
                                    'Accept': rdf.Format.mimetype(format)} )
    except Exception, msg:
      logging.error('SPARQL: %s, %s', msg, self.map_prefixes(prefixes) + sparql)
      raise

  def ask(self, where, params=None, graph=None, prefixes=None):
  #------------------------------------------------------------
    if params is None: params = {}
    return json.loads(self.query('ask where { %(graph)s { %(where)s } }'
                                 % dict(graph=('graph <%s>' % str(graph)) if graph else '',
                                        where=where % params),
                                 rdf.Format.JSON, prefixes)
                                )['boolean']

  def select(self, fields, where, params=None, graph=None, distinct=True, group=None, order=None, limit=None, prefixes=None):
  #--------------------------------------------------------------------------------------------------------------------------
    '''
    Get all items from a graph or repository.

    :param fields: The variables to be returned from the matched pattern.
    :type fields: str
    :param where: The graph pattern to match.
    :type where: str
    :param params: A dictionary of string format substitutions applied to the `where` argument.
    :param graph: The URI of an optional graph to query within.
    :param distinct: Ensure result sets are distinct. Defaults to True.
    :param group: The variable(s) to optional group the results by.
    :param order: The variable(s) to optional order the results.
    :param limit: Optionally limit the number of result sets.
    :type limit: str
    :param prefixes: A dictionary of namespace prefixes to use in the SPARQL query
    :type prefixes: dict
    :return: A list of dictionaries, keyed by selected field names, where each value
     is a dictionary about the result field, as per the 'bindings' list described in
     http://www.w3.org/TR/rdf-sparql-json-res/.
    :rtype: list
    '''
    if params is None: params = {}
    return json.loads(self.query(
              'select%(distinct)s %(fields)s where {\n %(graph)s {\n %(where)s }\n }%(group)s%(order)s%(limit)s'
                 % dict(distinct=' distinct' if distinct else '',
                        fields=fields % params,
                        graph=('graph <%s>' % graph) if graph else '',
                        where=where % params,
                        group=(' group by %s' % group) if group else '',
                        order=(' order by %s' % order) if order else '',
                        limit=(' limit %s' % limit) if limit else ''),
                 rdf.Format.JSON, prefixes)
        ).get('results', {}).get('bindings', [])

  def construct(self, template, where, params=None, graph=None, format=rdf.Format.RDFXML, prefixes=None):
  #------------------------------------------------------------------------------------------------------
    if params is None: params = {}
    return self.query('construct { %(tplate)s } %(graph)s where { %(where)s }'
                      % dict(tplate=template % params,
                             graph=('from <%s>' % str(graph)) if graph else '',
                             where=where % params),
                      format, prefixes)

  def describe(self, uri, graph=None, format=rdf.Format.RDFXML, prefixes=None):
  #----------------------------------------------------------------------------
    if uri == '':
      if graph is None: return ''
      uri = graph
      graph = None
    return self.construct(
      "<%(uri)s> ?op ?o . ?o a ?ot . ?s ?sp <%(uri)s> . ?s a ?st",
      "{ <%(uri)s> ?op ?o . optional { ?o a ?ot } } union { ?s ?sp <%(uri)s> . optional { ?s a ?st } }",
      params=dict(uri=uri), graph=graph, format=format)

  def update(self, sparql, prefixes=None):
  #---------------------------------------
    """
    Perform a SPARQL update.
    """
    ##logging.debug('UPD: %s', sparql)
    try:
      return self._request(self.ENDPOINTS[1], 'POST',
                           body=urllib.urlencode({self.UPDATE_PARAMETER: sparql + self.map_prefixes(prefixes)}),
                           headers={'Content-type': 'application/x-www-form-urlencoded'})
    except Exception, msg:
      logging.error('SPARQL: %s, %s', msg, sparql + self.map_prefixes(prefixes))
      raise


  def insert_triples(self, graph, triples, prefixes=None):
  #-------------------------------------------------------
    '''
    Insert a list of triples into a graph.
    '''
    if len(triples) == 0: return
##    sparql = ('insert data { graph <%(graph)s> { %(triples)s } }'   # 4store
    sparql = ('insert data in <%(graph)s> { %(triples)s }'            # Virtuoso
                % { 'graph': str(graph),
                    'triples': ' . '.join([' '.join(list(s)) for s in triples ]) })
    content = self.update(sparql, prefixes)
    if 'error' in content: raise Exception(content)

  def delete_triples(self, graph, triples, prefixes=None):
  #------------------------\-------------------------------
    '''
    Delete a list of triples from a graph.
    '''
    if len(triples) == 0: return
#    sparql = ('delete data { graph <%(graph)s> { %(triples)s } }'
    sparql = ('delete from graph <%(graph)s> { %(triples)s }'
                % { 'graph': graph,
                    'triples': ' . '.join([' '.join(list(s)) for s in triples ]) })
    content = self.update(sparql, prefixes)
    if 'error' in content: raise Exception(content)

  def update_triples(self, graph, triples, prefixes=None):
  #-------------------------------------------------------
    '''
    Remove all statements about the (subject, predicate) pairs in a list
    of triples from the graph then insert the triples.
    '''
    if len(triples) == 0: return
    last = (None, None)
    ##logging.debug('UPDATE: %s', triples)
    for s, p, o in sorted(triples):
      if (s, p) != last:
#        sparql = ('delete { graph <%(g)s> { %(s)s %(p)s ?o } } where { %(s)s %(p)s ?o }'
        sparql = ('delete from graph <%(g)s> { %(s)s %(p)s ?o } from <%(g)s> where { %(s)s %(p)s ?o }'
                    % {'g': str(graph), 's': s, 'p': p} )
        content = self.update(sparql, prefixes)
        if 'error' in content: raise Exception(content)
        last = (s, p)
    self.insert_triples(graph, triples, prefixes)  ###### DUPLICATES BECAUSE OF 4STORE BUG...


  def extend_graph(self, graph, statements, format=rdf.Format.RDFXML):
  #-------------------------------------------------------------------
    '''
    Extend an existing graph, creating one if not present.
    '''
    raise NotImplemented("SparqlStore.extend_graph()")

  def replace_graph(self, graph, statements, format=rdf.Format.RDFXML):
  #--------------------------------------------------------------------
    '''
    Replace an existing graph, creating one if not present.
    '''
    raise NotImplemented("SparqlStore.replace_graph()")

  def delete_graph(self, graph):
  #-----------------------------
    '''
    Delete an existing graph from the store.
    '''
    raise NotImplemented("SparqlStore.delete_graph()")



class Virtuoso(SparqlStore):
#===========================
  """
  Specifics for a Virtuoso SPARQL endpoint.

  A newly installed Virtuoso system requires:

  1. Permissions set on the database directory (INSTALL_DIR/var/lib/virtuoso/db)
     to allow write access by the user running Virtuoso.

  2. The INI file edited to increase limits for BufferSizes and MaxRows.

  3. The SPARQL_UPDATE role to be given to the SPARQL user.

  4. Full text search enabling using ISQL:::

     DB.DBA.RDF_OBJ_FT_RULE_ADD (null, null, 'All');

  5. Define additional namespace prefixes as required.


  ..warning::

    Virtuoso currently (V6.1.6) only supports RDFXML...

  """

  ENDPOINTS = [ '/sparql/', '/sparql/', '/sparql-graph-crud/' ]
  UPDATE_PARAMETER = 'query'


  def extend_graph(self, graph, statements, format=rdf.Format.RDFXML):
  #-------------------------------------------------------------------
    self._request(self.ENDPOINTS[2] + "?graph-uri=%s" % graph, 'POST',
                  body=statements, headers={'Content-Type': rdf.Format.mimetype(format)})

  def replace_graph(self, graph, statements, format=rdf.Format.RDFXML):
  #--------------------------------------------------------------------
    self._request(self.ENDPOINTS[2] + "?graph-uri=%s" % graph, 'PUT',
                  body=statements, headers={'Content-Type': rdf.Format.mimetype(format)})

  def delete_graph(self, graph):
  #-----------------------------
    self._request(self.ENDPOINTS[2] + "?graph-uri=%s" % graph, 'DELETE')



def FourStore(SparqlStore):
#==========================

  ENDPOINTS = [ '/sparql/', '/update/', '/data/' ]
  UPDATE_PARAMETER = 'update'

  def extend_graph(self, graph, statements, format=rdf.Format.RDFXML):
  #-------------------------------------------------------------------
    self._request(self.ENDPOINTS[2], 'POST',
                  body=urllib.urlencode({'data': statements,
                                         'graph': str(graph),
                                         'mime-type': rdf.Format.mimetype(format),
                                        }),
                  headers={'Content-type': 'application/x-www-form-urlencoded'})

  def replace_graph(self, graph, statements, format=rdf.Format.RDFXML):
  #--------------------------------------------------------------------
    self._request(self.ENDPOINTS[2] + "?graph=%s" % graph, 'PUT',
                  body=statements, headers={'Content-Type': rdf.Format.mimetype(format)})

  def delete_graph(self, graph):
  #-----------------------------
    self._request(self.ENDPOINTS[2] + "?graph=%s" % graph, 'DELETE')


  def fulltext(self):
  #------------------
    '''
    Enable stemming of rdfs:label, rdfs:comment, and dc:description text
    in 4store. See http://4store.org/trac/wiki/TextIndexing.
    '''
    self.extend_graph('system:config',
     """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix dc:   <http://purl.org/dc/elements/1.1/> .
        @prefix dct: <http://purl.org/dc/terms/> .
        @prefix text: <http://4store.org/fulltext#> .
        @prefix cnt: <http://www.w3.org/2011/content#> .

        rdfs:label      text:index text:stem .
        rdfs:comment    text:index text:stem .
        dc:description  text:index text:stem .
        dct:description text:index text:stem .
        cnt:chars       text:index text:stem .""")



if __name__ == '__main__':
#=========================

  def query(store, graph):
  #-----------------------
    print store.query("select * where { graph <%s> { ?s ?p ?o } }" % graph)

  rdf1 = """<?xml version="1.0" encoding="utf-8"?>
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                     xml:base="http://devel.biosignalml.org/provenance/example">
              <rdf:Description rdf:about="">
                <rdf:type rdf:resource="http://purl.org/net/provenance/ns#DataItem1"/>
              </rdf:Description>
            </rdf:RDF>"""

  rdf2 = """<?xml version="1.0" encoding="utf-8"?>
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                     xml:base="http://devel.biosignalml.org/provenance/example">
              <rdf:Description rdf:about="">
                <rdf:type rdf:resource="http://purl.org/net/provenance/ns#DataItem2"/>
              </rdf:Description>
            </rdf:RDF>"""

  graph = "http://devel.biosignalml.org/test/graph"

  store = Virtuoso("http://localhost:8890")


  print "RDF1 PUT"
  store.replace_graph(graph, rdf1)
  query(store, graph)

  print "\nRDF2 POST"
  store.extend_graph(graph, rdf2)
  query(store, graph)

  print "\nRDF2 PUT"
  store.replace_graph(graph, rdf2)
  query(store, graph)

  print "\nDELETE"
  store.delete_graph(graph)
  query(store, graph)

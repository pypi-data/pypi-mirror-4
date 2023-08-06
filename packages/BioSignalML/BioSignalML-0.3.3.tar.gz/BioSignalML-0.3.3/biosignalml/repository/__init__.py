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

import logging

import biosignalml.formats
from biosignalml import BSML, Recording, Signal, Event, Annotation
from biosignalml.rdf import DCT, PRV, Format
import biosignalml.rdf.sparqlstore as sparqlstore

from graphstore import GraphStore


class BSMLStore(GraphStore):
#===========================
  '''
  An RDF repository containing BioSignalML metadata.
  '''

  def __init__(self, base_uri, sparqlstore):
  #-----------------------------------------
    GraphStore.__init__(self, base_uri, BSML.RecordingGraph, sparqlstore)


  def has_recording(self, uri):
  #----------------------------
    ''' Check a URI refers to a Recording. '''
    return self.has_resource(uri, BSML.Recording)

  def has_signal(self, uri, graph_uri=None):
  #-----------------------------------------
    ''' Check a URI refers to a Signal. '''
    return self.has_resource(uri, BSML.Signal, graph_uri)

  def has_signal_in_recording(self, sig, rec):
  #-------------------------------------------
    ''' Check a URI refers to a Signal in a given Recording. '''
    g, r = get_graph_and_recording_uri(rec)
    return g is not none and self.has_signal(sig, g)

  def extend_recording(self, recording, abstractobject):
  #-----------------------------------------------------
    self._sparqlstore.extend_graph(recording.graph.uri,
      abstractobject.metadata_as_string(format=Format.RDFXML),
      format=Format.RDFXML)

  def recordings(self):
  #--------------------
    """
    Return a list of tuple(recording, graph) URIs in the repository.

    :rtype: list[(:class:`~biosignalml.rdf.Uri`, :class:`~biosignalml.rdf.Uri`)]
    """
    return self.get_resources(BSML.Recording)

  def add_recording_graph(self, uri, rdf, creator, format=Format.RDFXML):
  #----------------------------------------------------------------------
    return self.add_resource_graph(uri, BSML.Recording, rdf, creator, format=format)


  def get_graph_and_recording_uri(self, uri):
  #------------------------------------------
    """
    Get URIs of the Graph and Recording that contain the object.

    :param uri: The URI of some object.
    :return: The tuple (graph_uri, recording_uri)
    :rtype: tuple(:class:`~biosignalml.rdf.Uri`, :class:`~biosignalml.rdf.Uri`)
    """
    r = self.get_resources(BSML.Recording, condition='<%s> a []' % uri)
    return r[0] if r else (None, None)

  def get_recording(self, uri, graph_uri=None, **kwds):
  #----------------------------------------------------
    '''
    Get the Recording from the graph that an object is in.

    :param uri: The URI of some object.
    :param graph_uri: The URI of a named graph containing statements
      about the object.
    :rtype: :class:`~biosignalml.Recording`
    '''
    #logging.debug('Getting: %s', uri)
    if graph_uri is None: graph_uri, rec_uri = self.get_graph_and_recording_uri(uri)
    else: rec_uri = uri
    #logging.debug('Graph: %s', graph_uri)
    if graph_uri is not None:
      rclass = biosignalml.formats.CLASSES.get(
                 str(self.get_objects(rec_uri, DCT.format, graph=graph_uri)[0]),
                 Recording)
      graph = self.get_resource_as_graph(rec_uri, BSML.Recording, graph_uri)
      rec = rclass.create_from_graph(rec_uri, graph, signals=False, **kwds)
      return rec

  def get_recording_with_signals(self, uri, open_dataset=True, graph_uri=None):
  #----------------------------------------------------------------------------
    """
    Get the Recording with its Signals from the graph
      that an object is in.

    :param uri: The URI of some object.
    :param graph_uri: The URI of a named graph containing statements
      about the object.
    :param open_dataset: Try to open the recording's dataset. Optional, default True.
    :rtype: :class:`~biosignalml.Recording`
    """
    rec = self.get_recording(uri, graph_uri)
    if rec is not None:
      for r in self.select('?s', '?s a bsml:Signal . ?s bsml:recording <%(rec)s>',
          params=dict(rec=rec.uri), prefixes=dict(bsml=BSML.prefix), graph=rec.graph.uri, order='?s'):
        sig_uri = sparqlstore.get_result_value(r, 's')
        sig_graph = self.get_resource_as_graph(sig_uri, BSML.Signal, rec.graph.uri)
        rec.add_signal(rec.SignalClass.create_from_graph(sig_uri, sig_graph, units=None))
        rec.initialise(open_dataset=open_dataset)    ## This will open files...
    return rec


  def store_recording(self, recording, creator=None):
  #--------------------------------------------------
    """
    Store a recording's metadata in the repository.

    :param recording: The :class:`~biosignalml.Recording` to store.
    :param creator: Who or what is storing the recording.
    """
    return self.add_recording_graph(recording.uri,
      recording.metadata_as_graph().serialise(Format.RDFXML), creator, Format.RDFXML)


#  def signal_recording(self, uri):
#  #-------------------------------
#    return self.get_object(uri, BSML.recording)

  def get_signal(self, uri, graph_uri=None):
  #-----------------------------------------
    '''
    Get a Signal from the repository.

    :param uri: The URI of a Signal.
    :param graph_uri: An optional URI of the graph to query.
    :rtype: :class:`~biosignalml.Signal`
    '''
    # The following line works around a Virtuoso problem
    if graph_uri is None: graph_uri = self.get_graph_and_recording_uri(uri)[0]
    graph = self.get_resource_as_graph(uri, BSML.Signal, graph_uri)
    return Signal.create_from_graph(uri, graph, units=None)  # units set from graph...

#  def signal(self, sig, properties):              # In context of signal's recording...
#  #---------------------------------
#    if self.check_type(sig, BSML.Signal):
#      r = [ [ Graph.make_literal(t, '') for t in self.get_objects(sig, p) ] for p in properties ]
#      r.sort()
#      return r
#    else: return None

  def signals(self, rec_uri, graph_uri=None):
  #------------------------------------------
    '''
    Return a list of all Signals of a recording.

    :param uri: The URI of the recording.
    :param graph_uri: An optional URI of the graph to query.
    :rtype: list of bsml:Signal URIs
    '''
    return [ r[1]
      for r in self.get_resources(BSML.Signal, rvars='?r',
        condition='?r bsml:recording <%s>' % rec_uri,
        prefixes = dict(bsml=BSML.prefix),
        graph = graph_uri
        ) ]


  def get_event(self, uri, graph_uri=None):
  #-----------------------------------------
    '''
    Get an Event from the repository.

    :param uri: The URI of an Eventt.
    :param graph_uri: An optional URI of the graph to query.
    :rtype: :class:`~biosignalml.Event`
    '''
    # The following line works around a Virtuoso problem
    if graph_uri is None: graph_uri = self.get_graph_and_recording_uri(uri)[0]
    graph = self.get_resource_as_graph(uri, BSML.Event, graph_uri)
    for tm in graph.get_objects(uri, BSML.time):  ## This could be improved...
      graph.append_graph(self.get_resource_as_graph(tm.uri, BSML.Instant, graph_uri))
      graph.append_graph(self.get_resource_as_graph(tm.uri, BSML.Interval, graph_uri))
    return Event.create_from_graph(uri, graph)

  def events(self, rec_uri, eventtype=None, timetype=None, graph_uri=None):
  #------------------------------------------------------------------------
    '''
    Return a list of all Events associated with a recording.

    :param uri: The URI of the recording.
    :param eventtype: The type of events to find. Optional.
    :param graph_uri: An optional URI of the graph to query.
    :rtype: list of bsml:Event URIs
    '''

    if eventtype is None:
      condition =  '?r bsml:recording <%s>' % rec_uri
    else:
      condition = ('?r bsml:recording <%s> . ?r bsml:eventType <%s>'
                                  % (rec_uri, eventtype))
    if timetype is not None:
      condition += ' . ?r bsml:time ?tm . ?tm a <%s>' % timetype
    return [ r[1]
      for r in self.get_resources(BSML.Event, rvars='?r', condition=condition,
        prefixes=dict(bsml=BSML.prefix), graph=graph_uri)
      ]

  def eventtypes(self, rec_uri, counts=False, graph_uri=None):
  #-----------------------------------------------------------
    '''
    Return a list of all types of Events associated with a recording.

    :param uri: The URI of the recording.
    :param counts: Optionally return a count of each type of event.
    :param graph_uri: An optional URI of the graph to query.
    :rtype: list of bsml:Event URIs if no counts, otherwise tuple(URI, count).
    '''
    return [ tuple(r[1:3]) if counts else r[1]
      for r in self.get_resources(BSML.Event, rvars='?et count(?et) as ?count',
        condition = '?r bsml:recording <%s> . ?r bsml:eventType ?et' % rec_uri,
        group = '?et',
        prefixes = dict(bsml=BSML.prefix),
        graph = graph_uri
        ) ]


  def get_annotation(self, uri, graph_uri=None):
  #---------------------------------------------
    '''
    Get an Annotation from the repository.

    :param uri: The URI of an Annotation.
    :param graph_uri: An optional URI of the graph to query.
    :rtype: :class:`~biosignalml.Annotation`
    '''
    # The following line works around a Virtuoso problem
    if graph_uri is None: graph_uri = self.get_graph_and_recording_uri(uri)[0]
    graph = self.get_resource_as_graph(uri, BSML.Annotation, graph_uri)
    for tm in graph.get_objects(uri, BSML.time):  ## This could be improved...
      graph.append_graph(self.get_resource_as_graph(tm.uri, BSML.Instant, graph_uri))
      graph.append_graph(self.get_resource_as_graph(tm.uri, BSML.Interval, graph_uri))
    return Annotation.create_from_graph(uri, graph)

#  def get_annotation_by_content(self, uri, graph_uri=None):
#  #--------------------------------------------------------
#    '''
#    Get an Annotation from the repository identified by its body content.
#
#    :param uri: The URI of the body of an Annotation.
#    :rtype: :class:`~biosignalml.Annotation`
#    '''
#    if graph_uri is None: graph_uri = self.get_graph_and_recording_uri(uri)[0]
#    for r in self.select('?a', 'graph <%(g)s> { ?a a oa:Annotation . ?a oa:hasBody <%(u)s> }',
#                         params = dict(g=graph_uri, u=uri),
#                         prefixes = dict(oa = OA.prefix)):
#      return self.get_annotation(sparqlstore.get_result_value(r, 'a'), graph_uri)

  def annotations(self, uri, graph_uri=None):
  #------------------------------------------
    '''
    Return a list of all Annotations about a subject.

    :param uri: The URI of the subject.
    :param graph_uri: An optional URI of the graph to query.
    :rtype: list of bsml:Annotation URIs
    '''
    return [ r[1]
      for r in self.get_resources(BSML.Annotation, rvars='?r',
        condition='''?r dct:subject ?s . filter(regex(str(?s), "^%s(#.*)?$", "i")) .
              minus { [] prv:preceededBy ?r }''' % uri,
        prefixes = dict(dct=DCT.prefix, prv=PRV.prefix),
        graph = graph_uri
        ) ]

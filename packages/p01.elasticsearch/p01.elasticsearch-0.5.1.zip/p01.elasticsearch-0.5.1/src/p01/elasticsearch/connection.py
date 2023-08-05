##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import codecs
import datetime
import decimal
import httplib
import logging
import socket
import sys
import time
import urllib
import urlparse
from StringIO import StringIO
from httplib import HTTPConnection
from urllib import urlencode
from urlparse import urlsplit

import zope.interface

import p01.elasticsearch.exceptions
from p01.elasticsearch import interfaces
from p01.elasticsearch.exceptions import checkResponse

import json

_marker = object()


class SearchResponse(object):
    """Search response wrapper with simple query builder data."""

    def __init__(self, data, query, index, docType, **params):
        self.data = data
        self.query = query
        self.index = index
        self.docType = docType
        self.params = params
        # use start, from is is invalid in python
        self.start = params.get('from', 0)
        size = params.get('size', 0)
        self.size = size
        self.took = data.get('took')
        hits = data.get('hits', {})
        self.hits = hits.get('hits', {})
        self.total = hits.get('total', 0)
        self.maxScore = hits.get('max_score')
        # _scroll_id
#        self.scroller = data.get('_scroll_id')
        # pagination data support
        # get overall total based on query 
        # calculate pages
        if size == 0:
            self.pages = 1
        else:
            pages = self.total/size
            if pages == 0 or self.total % size:
                pages += 1
            self.pages = pages

    def __len__(self):
        """Return the number of matching documents contained in this set."""
        return len(self.hits)

    def __iter__(self):
        """Return an iterator of matching documents."""
        return iter(self.hits)

    def __repr__(self):
        return '<%s %s/%s/_search>' % (self.__class__.__name__, self.index,
            self.docType)


class JSONEncoder(json.JSONEncoder):
    """JSON encoder with knows how to handle datetime"""

    def default(self, value):
        if isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%S")
        elif isinstance(value, datetime.date):
            dt = datetime.datetime(value.year, value.month, value.day, 0, 0, 0)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        elif isinstance(value, decimal.Decimal):
            return float(str(value))
        else:
            return json.JSONEncoder.default(self, value)


class JSONDecoder(json.JSONDecoder):
    """JSON encoder with knows how to handle datetime"""

    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self.dict_to_object
        json.JSONDecoder.__init__(self, *args, **kwargs)

    def string_to_datetime(self, obj):
        """Decode a datetime string to a datetime object"""
        if isinstance(obj, basestring) and len(obj) == 19:
            try:
                return datetime.datetime(*obj.strptime("%Y-%m-%dT%H:%M:%S")[:6])
            except:
                pass
        return obj

    def dict_to_object(self, d):
        """Decode a datetime string to a datetime object"""
        for k, v in d.items():
            if isinstance(v, basestring) and len(v) == 19:
                try:
                    d[k] = datetime.datetime(
                        *time.strptime(v, "%Y-%m-%dT%H:%M:%S")[:6])
                except ValueError:
                    pass
            elif isinstance(v, list):
                d[k] = [self.string_to_datetime(elem) for elem in v]
        return d


class ElasticSearchConnection(object):
    """ElasticSearch client with threading server pool with http connections."""

    zope.interface.implements(interfaces.IElasticSearchConnection)

    def __init__(self, serverPool, searchResponseFactory=SearchResponse,
        maxRetries=None, autoRefresh=False, autoRefreshTimeout=30,
        bulkMaxSize=400, encoder=_marker, decoder=_marker):
        self.serverPool = serverPool
        self.searchResponseFactory = searchResponseFactory
        self._server = None
        self.conn = None
        self.maxRetries = maxRetries
        self.autoRefresh = autoRefresh
        self.autoRefreshTimeout = autoRefreshTimeout
        self.refreshed = True
        self.reconnects = 0
        # json en/decoder
        if encoder is _marker:
            encoder = JSONEncoder
        self.encoder = encoder
        if decoder is _marker:
            decoder = JSONDecoder
        self.decoder = decoder
        # bulk support
        self.bulkMaxSize = bulkMaxSize
        self.bulkItems = []
        self.bulkCounter = 0
        # scroll id
        self.scroller = None

    # connection
    def close(self):
        self.server.close()

    def reConnect(self):
        self.reconnects += 1
        self.server.close()
        self.server.connect()

    @property
    def connectTime(self):
        return self.server.connectTime

    @property
    def server(self):
        """Get the next server from the server pool"""
        if self._server is None or self._server.isDead:
            self._server = self.serverPool.get()
        return self._server

    def jsonDumps(self, obj):
        """Dumps json data"""
        return json.dumps(obj, cls=self.encoder)

    def jsonLoads(self, jsonStr):
        """Loads json data"""
        return json.loads(jsonStr, cls=self.decoder)

    # internal helpers
    def _makePath(self, parts, allowMultiParts=True):
        """Build a path based o the given parts"""
        res = []
        append = res.append
        for part in parts:
            if part is None:
                continue
            if isinstance(part, list):
                part = ','.join(part)
            append(str(part))
        path = '/'.join(res)
        if not allowMultiParts and ',' in path:
            raise ValueError("Multi part index or docType are not allowed")
        if not path.startswith('/'):
            path = '/'+path
        return path

    def _sendRequest(self, method, path, body=None, params={}):
        """Send a GET, POST, PUT etc request based on the given arguments"""
        if params:
            path = "?".join([path, urlencode(params)])
        if body is not None:
            # body could be a basestring or dict
            if isinstance(body, dict):
                # convert a dict
                body = self.jsonDumps(body)
        else:
            body = ""
        logging.info("making %s request to path: %s:%s/%s with body: %s" % (
            method, self.server.host, self.server.port, path, body))
        maxRetries = self.maxRetries or len(self.serverPool.aliveServers)
        while maxRetries:
            maxRetries -= 1
            try:
                response = self.server.request(method, path, body)
                return checkResponse(response)
            except (socket.timeout, socket.error,
                    httplib.ImproperConnectionState,
                    httplib.BadStatusLine), e:
                self.serverPool.markDead(self.server)
                if not maxRetries:
                    raise e

        raise p01.elasticsearch.exceptions.NoServerAvailable

    def _sendQuery(self, method, query, path, **params):
        """Helper method for search and count calls"""
        if self.autoRefresh and self.refreshed == False:
            self.refresh(indexes, self.autoRefreshTimeout)
        body = None
        if isinstance(query, basestring):
            # basestring query get processed as url query string
            params['q'] = query
        else:
            # dict query get processed as json body data
            body = query
        return self._sendRequest(method, path, body, params)

    # REST API
    def index(self, doc, index, docType, id=_marker, **params):
        """Index a document into a specific index and make it searchable."""
        self.refreshed = False
        if id is None:
            method = 'POST'
        else:
            method = 'PUT'
        # use an existing doc _id as id
        _id = doc.get('_id', None)
        if _id is None and id is _marker:
                raise ValueError(
                    "You must explicit define id=None without doc['_id']")
        if _id is not None and id is not _marker:
            raise ValueError("Can't use an id and doc['_id'] at the same time")
        if _id is not None:
            id = _id
        path = self._makePath([index, docType, id], allowMultiParts=False)
        response = self._sendRequest(method, path, doc, params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def get(self, id, index, docType, **params):
        """Get a document from an index based on the given id"""
        path = self._makePath([index, docType, id])
        response = self._sendRequest('GET', path, params=params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def count(self, query, index=None, docType=None, **params):
        """Execute a query against one or more indices and get hits count"""
        if index is None and docType is not None:
            index = '_all'
        path = self._makePath([index, docType, '_count'])
        response = self._sendQuery('GET', query, path, **params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def doSearch(self, query, index=None, docType=None, **params):
        """Execute a search query against one or more indices and one or more
        docType supporting additional filter etc as params key/values. This
        method returns the raw json data
        """
        if index is None and docType is not None:
            index = '_all'
        path = self._makePath([index, docType, '_search'])
        response = self._sendQuery('GET', query, path, **params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def getScroller(self, query, index=None, docType=None, size=50,
        scroll='10m', **params):
        """Get _scroll_id for the given search query"""
        params['search_type'] = 'scan'
        params['scroll'] = scroll
        params['size'] = size
        data = self.doSearch(query, index, docType, **params)
        # setup and return scroller
        self.scroller = data.get('_scroll_id')
        return self.scroller

    def doScroll(self, scroller=None, scroll="10m"):
        """Scrolling search results based on a given an scroll id (scroller)

        Note: this method will setup a new _scroll_id as scroller if we have
        results. If we don't get results, which means scrolling is finished
        and the method will set the scroller to None.

        Note: this method doss only scroll one iteration. See scroll method for
        scroll the full scan or use the scan method for od exverything implicit.

        """
        # scroll search hits as long as we have a scroller
        self.scroller = scroller
        params = {'scroll': scroll}
        if self.scroller is not None:
            response = self._sendRequest('GET', '_search/scroll', self.scroller,
                params)
            jsonStr = response.read()
            data = self.jsonLoads(jsonStr)
            # setup new scroller
            self.scroller = data.get('_scroll_id')
            hits = data.get('hits', {}).get('hits')
            if hits:
                for doc in hits:
                    yield doc
            else:
                # abort implicit scrolling by set scroller to None
                self.scroller = None

    def scroll(self, scroller=None, scroll="10m"):
        """Scrolling search results based on given scroll id (scroller)
        
        This method will use doScroll and scroll the result till no hits will
        get returned

        """
        # setup new scroller
        self.scroller = scroller
        # scroll search hits as long as we get hits from doScroll
        while self.scroller is not None:
            # call doScroll as long as self.scroller is not None
            for doc in self.doScroll(self.scroller, scroll):
                yield doc

    def search(self, query, index=None, docType=None, **params):
        """Execute a search query against one or more indices and one or more
        docType supporting additional filter etc as params key/values.

        Note: you must explicit set search_type=scan params for scan search.

        Note: a scan search will only return documents and not a search
        response factory wrapper.
        
        See scan method for an explicit scan search type call or use
        getScroller, scroll or getScroller and doScroll for even more explicit
        scan search processing.

        """
        data = self.doSearch(query, index, docType, **params)
        # setup scroller if given
        scroller = data.get('_scroll_id')
        if scroller is not None:
            # scroll search hits
            scroll = params.get('scroll', '10m')
            return self.scroll(scroller, scroll)
        else:
            return self.searchResponseFactory(data, query, index, docType,
                **params)

    def scan(self, query, index=None, docType=None, size=50, scroll='10m',
        **params):
        """Support scan search without explicit given params"""
        scroller = self.getScroller(query, index, docType, size, scroll='10m',
            **params)
        return self.scroll(scroller, scroll)

    def getBatchData(self, query, index=None, docType=None, page=1, size=25,
        **params):
        """Returns batched elasticsearch response, current page, total items
        and page size.

        Note: the page can get recalculated if the page position doesn't fit
        into the batch. This means the page in the reult can be different as
        the given page input. This is usefull if we use a larger page number
        as we realy have, e.g. after remove an item.

        """
        # the first pagination page starts with 1 and not 0 (zero)
        if page < 1:
            # ensure starting with page 1
            page = 1
        if size < 1:
            # prevent negative numbers
            size = 1
        params['from'] = start = (page-1) * size
        params['size'] = size
        # start with search, this allows us to approve the page position
        response = self.search(query, index, docType, **params)

        # get overall total based on query
        total = response.total 
        # calculate pages
        pages = total/size
        if pages == 0 or total % size:
            pages += 1
        # as next we approve our page position
        if page > pages:
            # restart with pages number as page which is the last page
            page = pages
            # remove params, we will calculate them later again
            params.pop('from')
            params.pop('size')
            return self.getBatchData(query, index, docType, page, size,
                **params)

        # return data including probably adjusted page number
        return (response, page, pages, total)

    def delete(self, id, index, docType, **params):
        """Delete a document from a specific index based on its id"""
        path = self._makePath([index, docType, id], allowMultiParts=False)
        response = self._sendRequest('DELETE', path, params=params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def deleteByQuery(self, query, index, docType, **params):
        """Delete a document from a specific index based on its id"""
        path = self._makePath([index, docType, '_query'], allowMultiParts=False)
        response = self._sendQuery('DELETE', query, path, **params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def moreLikeThis(self, id, index, docType, **params):
        """Execute a "more like this" search query against one or more fields
        """
        path = self._makePath([index, docType, id, '_mlt'])
        response = self._sendRequest('GET', path, params=params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def flush(self, index=None, **params):
        """Flushes one or more indices (clear memory)"""
        self.bulkCommit()
        path = self._makePath([index, '_flush'])
        response = self._sendRequest('POST', path, params=params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def refresh(self, index=None, timeout=30):
        """Refresh one or more indices"""
        self.bulkCommit()
        path = self._makePath([index, '_refresh'])
        response = self._sendRequest('POST', path)
        jsonStr = response.read()
        # read response first before we start a cluster healt request
        self.clusterHealth(wait_for_status='green', timeout=timeout)
        self.refreshed = True
        return self.jsonLoads(jsonStr)

    # settings
    def getSettings(self, index=None):
        """Retrieve the settings of one or more indices"""
        path = self._makePath([index, '_settings'])
        response = self._sendRequest('GET', path)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def putSettings(self, settings, index=None, **params):
        """Register specific settings definition for a specific type against
        one or more indices.
        """
        path = self._makePath([index, "_settings"])
        response = self._sendRequest('PUT', path, settings, params=params)
        jsonStr = response.read()
        self.refreshed = False
        return self.jsonLoads(jsonStr)

    # mapping API
    def putMapping(self, mapping, index, docType, **params):
        """Register specific mapping definition for a specific type against one
        or more indices.
        """
        path = self._makePath([index, docType, "_mapping"])
        response = self._sendRequest('PUT', path, mapping, params=params)
        jsonStr = response.read()
        self.refreshed = False
        return self.jsonLoads(jsonStr)

    def getMapping(self, index=None, docType=None):
        """Get specific mapping definition for a specific type against one
        or more index and one or more docTyp.
        """
        path = self._makePath([index, docType, "_mapping"])
        response = self._sendRequest('GET', path)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def deleteMapping(self, index, docType=None, **params):
        """Register specific mapping definition for a specific type against one
        or more indices.
        """
        raise NotImplementedError("deleteMapping is not implemented yet")

    # buld API
    def bulk(self, opType, index, docType, doc=None, id=None, parent=None,
        **params):
        """Index a document into a specific index and make it searchable."""
        # condition
        if opType == 'delete' and doc is not None:
            raise ValueError("Can't use doc with op_type delete")
        # 
        if opType == 'delete' and id is None:
            raise ValueError("Missing id used with op_type delete")

        self.refreshed = False
        if opType not in ['index', 'create', 'delete']:
            raise TypeError("Only create, index and delete allowed as op_type")
        # build command
        cmd = {opType : {"_index": index, "_type": docType}}
        if parent is not None:
            cmd[opType]['_parent'] = parent
        if id is not None:
            cmd[opType]['_id'] = id
        # append command
        self.bulkItems.append(cmd)
        if opType in ['index', 'create']:
            # append doc if command not delete
            self.bulkItems.append(doc)
        self.bulkCounter += 1
        return self.bulkFlush()

    def bulkCreate(self, doc, index, docType, id=None, parent=None, **params):
        """Create a document in a specific index and make it searchable."""
        return self.bulk('create', index, docType, doc, id, parent,
            params=params)

    def bulkIndex(self, doc, index, docType, id=None, parent=None, **params):
        """Index a document in a specific index and make it searchable."""
        return self.bulk('index', index, docType, doc, id, parent,
            params=params)

    def bulkDelete(self, index, docType, id=None, parent=None, **params):
        """Delete a document from a specific index."""
        return self.bulk('delete', index, docType, None, id, parent,
            params=params)

    def bulkFlush(self, forced=False):
        """Wait to process all pending operations"""
        if not forced and self.bulkCounter < self.bulkMaxSize:
            return
        return self.bulkCommit()

    def bulkCommit(self):
        """Force executing of all bulk data"""
        if not self.bulkItems:
            return
        sio = StringIO()
        for item in self.bulkItems:
            sio.write(self.jsonDumps(item))
            sio.write("\n")
        body = sio.getvalue()
        response = self._sendRequest("POST", "/_bulk", body)
        self.bulkItems = []
        self.bulkCounter = 0
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    # index management API
    def status(self, index=None):
        """Retrieve the status of one or more indices"""
        path = self._makePath([index, '_status'])
        response = self._sendRequest('GET', path)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def analyze(self, text, index, analyzer=None, **params):
        """Performs the analysis process on a text and return the tokens
        breakdown of the text.
        
        Use text or None and params['text'] as text value. If text is given
        it will get used as request body and if text is given as params
        key/value the text is used as request query string.

        """
        path = self._makePath([index, '_analyze'])
        body = text
        if analyzer is not None:
            params['analyzer'] = analyzer
        response = self._sendRequest('GET', path, body, params=params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def createIndex(self, index, mappings=None, settings=None, timeout=30):
        """Creates an index with optional mapping and settings.

        Settings must be a dictionary which will be converted to JSON.
        Elasticsearch also accepts yaml, but we are only passing JSON.
        """
        data = {}
        if settings:
            data['settings'] = settings
        if mappings:
            data['mappings'] = mappings
        response = self._sendRequest('PUT', index, data)
        jsonStr = response.read()
        self.refreshed = False
        if timeout:
            self.refresh(index, timeout)
        return self.jsonLoads(jsonStr)

    def deleteIndex(self, index):
        """Deletes an index."""
        response = self._sendRequest('DELETE', index)
        self.refreshed = False
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def closeIndex(self, index):
        """Close an index"""
        return self._sendRequest('POST', "/%s/_close" % index)

    def openIndex(self, index):
        """Open an index"""
        return self._sendRequest('POST', "/%s/_open" % index)

    def gatewaySnapshot(self, index=None):
        """Gateway snapshot one or more indices"""
        path = self._makePath([index, '_gateway', 'snapshot'])
        response = self._sendRequest('POST', path)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def optimize(self, index=None, max_num_segments=None,
        only_expunge_deletes=False, refresh=True, flush=True,
        wait_for_merge=False):
        """Optimize one ore more indices

        index -- one or more indexes as string separated by coma

        max_num_segments -- The number of segments to optimize to. To fully
          optimize the index, set it to 1. Defaults to simply checking if a
          merge needs to execute, and if so, executes it.

        only_expunge_deletes -- Should the optimize process only expunge
          segments with deletes in it. In Lucene, a document is not deleted
          from a segment, just marked as deleted. During a merge process of
          segments, a new segment is created that does have those deletes.
          This flag allow to only merge segments that have deletes.
          Defaults to false. 

        refresh -- Should a refresh be performed after the optimize. Defaults
          to true.  

        flush -- Should a flush be performed after the optimize. Defaults to
          true.  

        wait_for_merge -- Should the request wait for the merge to end. 
          Defaults to true. Note, a merge can potentially be a very heavy
          operation, so it might make sense to run it set to false.

        """
        path = self._makePath([index, '_optimize'])
        params = dict(
            wait_for_merge=wait_for_merge,
            only_expunge_deletes=only_expunge_deletes,
            refresh=refresh,
            flush=flush,
        )
        if max_num_segments is not None:
            params['max_num_segments'] = max_num_segments
        response = self._sendRequest('POST', path, params=params)
        self.refreshed = True
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    # cluster API
    def clusterHealth(self, level="cluster", index=None, wait_for_status=None,
        wait_for_relocating_shards=None, wait_for_nodes=None, timeout=31):
        """Returns the cluster state

        Request Parameters

        The cluster health API accepts the following request parameters:

        level -- Can be one of cluster, indices or shards. Controls the details 
          level of the health information returned. Defaults to cluster.

        wait_for_status -- One of green, yellow or red. Will wait
          (until the timeout provided) until the status of the cluster changes
          to the one provided. By default, will not wait for any status.

        wait_for_relocating_shards -- A number controlling to how many
          relocating shards to wait for. Usually will be 0 to indicate to wait
          till all relocation have happened. Defaults to not to wait.

        wait_for_nodes -- The request waits until the specified number N of
          nodes is available.

        timeout -- A time based parameter controlling how long to wait if one
          of the wait_for_XXX are provided. Defaults to 31s. Also take a  look
          at the refresh and connection timeout

        """
        path = self._makePath(['_cluster', 'health', index])
        params = {}
        if level not in ["cluster", "indices", "shards"]:
            raise ValueError("Invalid level: %s" % level)
        params['level'] = level

        if wait_for_status is not None:
            if wait_for_status not in ["green", "yellow", "red"]:
                raise ValueError("Invalid wait_for_status: %s" % wait_for_status)
            params['wait_for_status'] = wait_for_status
            params['timeout'] = "%ds" % timeout
        if wait_for_relocating_shards is not None:
            raise ValueError(
                "wait_for_relocating_shards argument is not supported yet")
        if wait_for_nodes is not None:
            raise ValueError(
                "wait_for_nodes argument is not supported yet")
        response = self._sendRequest('GET', path, params=params)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def clusterState(self, filter_nodes=False, filter_routing_table=False,
        filter_metadata=False, filter_blocks=False, filter_indices=None):
        """Returns the cluster state

        filter_nodes -- Set to true to filter out the nodes part of the
          response

        filter_routing_table -- Set to true to filter out the routing_table
          part of the response.

        filter_metadata -- Set to true to filter out the metadata part of the
          response

        filter_blocks -- Set to true to filter out the blocks part of the
          response

        filter_indices -- When not filtering metadata, a comma separated list
          of indices to include in the response

        """
        params = {}
        if filter_nodes:
            params['filter_nodes'] = 'true'
        if filter_routing_table:
            params['filter_routing_table'] = 'true'
        if filter_metadata:
            params['filter_metadata'] = 'true'
        if filter_blocks:
            params['filter_blocks'] = 'true'
        if filter_indices:
            params['filter_indices'] = filter_indices

        response = self._sendRequest('GET', "/_cluster/state")
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def clusterNodesInfo(self, nodes=None):
        """Returns the node infos for one or more nodes"""
        parts = ["_cluster", "nodes"]
        if nodes is not None:
            if not isinstance(nodes, list):
                nodes = [nodes]
            parts.append(','.join(nodes))
        path = self._makePath(parts)
        response = self._sendRequest('GET', path)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def clusterNodesStats(self, nodes=None):
        """Returns the node stats for one or more nodes"""
        parts = ["_cluster", "nodes"]
        if nodes is not None:
            if not isinstance(nodes, list):
                nodes = [nodes]
            parts.append(','.join(nodes))
        parts.append('stats')
        path = self._makePath(parts)
        response = self._sendRequest('GET', path)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def clusterNodesShutDown(self, nodes=None):
        """Shutdown one or more (or all) nodes in the cluster."""
        parts = ["_cluster", "nodes"]
        if nodes is not None:
            if not isinstance(nodes, list):
                nodes = [nodes]
            parts.append(','.join(nodes))
        parts.append('_shutdown')
        path = self._makePath(parts)
        response = self._sendRequest('GET', path)
        jsonStr = response.read()
        return self.jsonLoads(jsonStr)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.serverPool.info)

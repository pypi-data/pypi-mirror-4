##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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

import zope.interface
import zope.schema


class IElasticSearchConnectionPool(zope.interface.Interface):
    """ElasticSearch connection pool"""

    connection = zope.interface.Attribute('ElasticSearchConnection instance')

    def reset():
        """Reset the elasticsearch connection."""
        

class IElasticSearchConnection(zope.interface.Interface):
    """ElasticSearch connection"""

    def close():
        """Close the elasticsearch server connection."""

    def reConnect():
        """Reconnect with the elasticsearch server."""

    # REST API
    def index(doc, index, docType, id, **params):
        """Index a document into a specific index and make it searchable."""

    def get(id, index, docType, **params):
        """Get a document from an index based on the given id"""

    def count(query, index=None, docType=None, **params):
        """Execute a query against one or more indices and get hits count"""
    def search(query, index=None, docType=None, **params):
        """Execute a search query against one or more indices and one or more
        docType supporting additional filter etc as params key/values
        """

    def getBatchData(query, index=None, docType=None, page=1, size=25,
        **params):
        """Returns batched elasticsearch response, current page, total items
        and page size.

        Note: the page can get recalculated if the page position doesn't fit
        into the batch. This means the page in the reult can be different as
        the given page input. This is usefull if we use a larger page number
        as we realy have, e.g. after remove an item.

        """

    def delete(id, index, docType, **params):
        """Delete a document from a specific index based on its id"""

    def deleteByQuery(query, index, docType, **params):
        """Delete a document from a specific index based on its id"""

    def moreLikeThis(id, index, docType, **params):
        """Execute a "more like this" search query against one or more fields
        """

    def flush(index=None, **params):
        """Flushes one or more indices (clear memory)"""

    def refresh(index=None, timeout=30):
        """Refresh one or more indices"""

    # mapping API
    def putMapping(mapping, index, docType, **params):
        """Register specific mapping definition for a specific type against one
        or more indices.
        """

    def getMapping(index=None, docType=None):
        """Get specific mapping definition for a specific type against one
        or more index and one or more docTyp.
        """

    def deleteMapping(index, docType=None, **params):
        """Register specific mapping definition for a specific type against one
        or more indices.
        """

    # buld API
    def bulk(opType, index, docType, doc=None, id=None, parent=None,
        **params):
        """Index a document into a specific index and make it searchable."""

    def bulkCreate(doc, index, docType, id=None, parent=None, **params):
        """Create a document in a specific index and make it searchable."""

    def bulkIndex(doc, index, docType, id=None, parent=None, **params):
        """Index a document in a specific index and make it searchable."""

    def bulkDelete(index, docType, id=None, parent=None, **params):
        """Delete a document from a specific index."""

    def bulkFlush(forced=False):
        """Wait to process all pending operations"""

    def bulkCommit(self):
        """Force executing of all bulk data"""

    # index management API
    def status(index=None):
        """Retrieve the status of one or more indices"""

    def analyze(text, index, analyzer=None, **params):
        """Performs the analysis process on a text and return the tokens
        breakdown of the text.
        
        Use text or None and params['text'] as text value. If text is given
        it will get used as request body and if text is given as params
        key/value the text is used as request query string.

        """

    def createIndex(index, mappings=None, settings=None, timeout=30):
        """Creates an index with optional mapping and settings.

        Settings must be a dictionary which will be converted to JSON.
        Elasticsearch also accepts yaml, but we are only passing JSON.
        """

    def deleteIndex(index):
        """Deletes an index."""

    def closeIndex(index):
        """Close an index"""

    def openIndex(index):
        """Open an index"""

    def gatewaySnapshot(index=None):
        """Gateway snapshot one or more indices"""

    def optimize(index=None, max_num_segments=None,
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

    # settings
    def getSettings(index=None):
        """Retrieve the settings of one or more indices"""

    # cluster API
    def clusterHealth(level="cluster", index=None, wait_for_status=None,
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

    def clusterState(filter_nodes=False, filter_routing_table=False,
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

    def clusterNodesInfo(nodes=None):
        """Returns the node infos for one or more nodes"""

    def clusterNodesStats(nodes=None):
        """Returns the node stats for one or more nodes"""

    def clusterNodesShutDown(nodes=None):
        """Shutdown one or more (or all) nodes in the cluster."""

#class IElasticSearchResponse(zope.interface.Interface):
#    """ElasticSearch response."""
#
#    def __len__():
#        """Return the number of matching documents contained in this set."""
#
#    def __iter__():
#        """Return an iterator of matching documents."""

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

import re
import pprint

import p01.elasticsearch.connection
import p01.elasticsearch.pool


###############################################################################
#
# test helper methods
#
###############################################################################

class RENormalizer(object):
    """Normalizer which can convert text based on regex patterns"""

    def __init__(self, patterns):
        self.patterns = patterns
        self.transformers = map(self._cook, patterns)

    def _cook(self, pattern):
        if callable(pattern):
            return pattern
        regexp, replacement = pattern
        return lambda text: regexp.sub(replacement, text)

    def addPattern(self, pattern):
        patterns = list(self.patterns)
        patterns.append(pattern)
        self.transformers = map(self._cook, patterns)
        self.patterns = patterns

    def __call__(self, data):
        """Normalize a dict or text"""
        if not isinstance(data, basestring):
            data = pprint.pformat(data)
        for normalizer in self.transformers:
            data = normalizer(data)
        return data

    def pprint(self, data):
        """Pretty print data"""
        print self(data)


# see sample.txt for usage
statusRENormalizer = RENormalizer([
   (re.compile("u'id': [a-zA-Z0-9.]+"), "u'id': ..."),
   (re.compile("u'num_docs': [0-9]+"), "u'num_docs': ..."),
   (re.compile("u'node': u'[a-zA-Z0-9._-]+'"), "u'node': u'...'"),
   (re.compile("u'max_doc': [0-9]+"), "u'max_doc': ..."),
   (re.compile("u'primary_size': u'[a-zA-Z0-9.]+'"), "u'primary_size': u'...'"),
   (re.compile("u'primary_size_in_bytes': [a-zA-Z0-9.]+"),
               "u'primary_size_in_bytes': ..."),
   (re.compile("u'size': u'[a-zA-Z0-9.]+'"), "u'size': u'...'"),
   (re.compile("u'size_in_bytes': [0-9.]+"), "u'size_in_bytes': ..."),
   (re.compile("u'total_time': u'[a-zA-Z0-9.]+'"), "u'total_time': u'...'"),
   (re.compile("u'total_time_in_millis': [0-9.]+"),
               "u'total_time_in_millis': ..."),
   (re.compile("u'location': \[-?[0-9.]+, -?[0-9.]+\]"),
               "u'location': [..., ...]"),
   (re.compile("u'refresh': {u'total': [0-9.]+,"),
               "u'refresh': {u'total': ...,"),
   ])

searchRENormalizer = RENormalizer([
   (re.compile("u'took': [0-9]+"), "u'took': ..."),
   ])


def getTestConnection(host='localhost', port='45299'):
    """Retruns a fresh connection which prevents to reuse an old one from
    another thread.
    """
    servers = ['%s:%s' % (host, port)]
    serverPool = p01.elasticsearch.pool.ServerPool(servers) 
    conn = p01.elasticsearch.connection.ElasticSearchConnection(serverPool)
    conn.close()
    return conn

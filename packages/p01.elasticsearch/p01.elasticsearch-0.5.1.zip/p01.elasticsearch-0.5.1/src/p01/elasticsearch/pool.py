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

import sys
import threading
import time
import logging
import urlparse
import httplib

from thrift import Thrift
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from thriftconnector import Rest
from thriftconnector.ttypes import Method, RestRequest

import zope.interface

from p01.elasticsearch import interfaces
from p01.elasticsearch import connection
import p01.elasticsearch.exceptions

log = logging.getLogger('p01.elasticsearch')

import socket
# on some platforms, there is no AI_ADDRCONFIG
# in the socket module... monkey patch it in or thrift will complain
if not getattr(socket, 'AI_ADDRCONFIG', False):
    socket.AI_ADDRCONFIG = 0


class Server(object):
    """Server (client) supporting thread local http connections"""

    def __init__(self, host, port, timeout=None):
        # static values
        self.host = host
        self.port = int(port)
        self.timeout = timeout
        # static using RLock for change
        self.retryTime = 0
        # thread local values
        self._local = threading.local()
        self._local.connectTime = 0

    @property
    def isDead(self):
        if self.retryTime and self.retryTime > time.time():
            return True
        else:
            return False

    @property
    def connectTime(self):
        if not getattr(self._local, 'connectTime', None):
            self._local.connectTime = time.time()
        return self._local.connectTime

    def connect(self):
        if not getattr(self._local, 'conn', None):
            self._local.connectTime = time.time()
            self._local.conn = httplib.HTTPConnection(self.host, self.port,
                timeout=self.timeout)

    def request(self, method, path, body):
        self.connect()
        self._local.conn.request(method, path, body)
        return self._local.conn.getresponse()

    def close(self):
        try:
            self._local.conn.close()
        except AttributeError, e:
            # conn not set yet
            pass

    def __repr__(self):
        return '<%s timeout: %s %s:%s>' % (self.__class__.__name__, self.host,
            self.port, self.timeout) 


class RestResponseWrapper(object):
    """
    Wrap the thrift RestResponse into something that
    matches the HTTPConnection response we use in http code.
    """

    def __init__(self, RestResponse):
        self.RestResponse = RestResponse

    def read(self):
        return self.RestResponse.body

    @property
    def reason(self):
        return 'unknown'

    @property
    def status(self):
        return self.RestResponse.status

class ThriftServer(Server):

    def connect(self):
        """Create new connection unless we already have one."""
        if not getattr(self._local, 'conn', None):
            transport = TSocket.TSocket(self.host, self.port)
            if self.timeout:
                transport.setTimeout(self.timeout * 1000) # milliseconds
            transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
            client = Rest.Client(protocol)
            transport.open()
            self._local.conn = client
            self._local.transport = transport

    def request(self, method, path, body, params={}, headers={}):
        """
        Create a request, run it and return the response.
        """
        request = RestRequest(method=Method._NAMES_TO_VALUES[method.upper()],
                  uri=path, parameters=params, headers=headers, body=body)
        self.connect()
        RestResponse = self._local.conn.execute(request)
        return RestResponseWrapper(RestResponse)

    def close(self):
        try:
            self._local.transport.close()
        except AttributeError, e:
            # conn not set yet
            pass


class ServerPool(object):
    """Shared server pool we can choose from"""

    def __init__(self, serverOrServers, retryDelay=10, timeout=None, thrift=False):
        self._lock = threading.RLock()
        if not isinstance(serverOrServers, list):
            serverOrServers = [serverOrServers]
        self._aliveServers = []
        for data in serverOrServers:
            info = data.split(':')
            if thrift:
                server = ThriftServer(info[0], info[1], timeout=timeout)
            else:
                server = Server(info[0], info[1], timeout=timeout)
            self._aliveServers.append(server)
        self.retryDelay = retryDelay
        self.deadServers = []
        
    @property
    def info(self):
        return ', '.join(['%s:%s' % (s.host, s.port) for s in self.aliveServers])

    @apply
    def aliveServers():
        def fget(self):
            if self.deadServers:
                with self._lock:
                    server = self.deadServers.pop()
                    if server.isDead:
                        # not yet, put it back
                        self.deadServers.append(server)
                    else:
                        self._aliveServers.append(server)
                        log.info('Server %r reinstated into working pool', server)
            return self._aliveServers
        def fset(self, aliveServers):
            with self._lock:
                self._aliveServers = aliveServers
        return property(fget, fset)

    def get(self):
        with self._lock:
            if not self.aliveServers:
                log.critical('No servers available')
                raise p01.elasticsearch.exceptions.NoServerAvailable()
            # get first server
            server = self.aliveServers.pop(0)
            # append as last server
            self.aliveServers.append(server)
            # return choosen server
            return server

    def markDead(self, server):
        with self._lock:
            server.retryTime = time.time() + self.retryDelay
            self._aliveServers.remove(server)
            self.deadServers.insert(0, server)

    def __repr__(self):
        return '<%s retryDelay:%s %s>' % (self.__class__.__name__,
            self.retryDelay, self.info)


class ElasticSearchConnectionPool(object):
    """ElasticSearch connection pool.
    
    ElasticSearch connection pool can get used as a singleton instance or a
    a global named utility and knows how to setup a thread safe elasticsearch
    connection instance.

    """

    zope.interface.implements(interfaces.IElasticSearchConnection)

    reConnectIntervall = 60 # max time in seconds till we reconnect

    def __init__(self, serverPool,
        connectionFactory=connection.ElasticSearchConnection,
        searchResponseFactory=connection.SearchResponse, logLevel=0):
        self.serverPool = serverPool
        self.searchResponseFactory = searchResponseFactory
        self.connectionFactory = connectionFactory
        self.key = 'p01.elasticsearch-%s' % id(self.serverPool)
        self.logLevel = logLevel
        self._local = threading.local()

    def close(self):
        conn = getattr(self._local, 'conn', None)
        if conn is not None:
            self._local.conn.close()

    @property
    def connection(self):
        conn = getattr(self._local, 'conn', None)
        if conn is None:
            conn = self.connectionFactory(self.serverPool,
                self.searchResponseFactory)
            self._local.conn = conn
            if self.logLevel:
                log.log(self.logLevel,
                    "Create connection for %s" % self.serverPool.info)

        if getattr(conn, 'connectTime', None):
            # only calculate if connectTime is given
            now = time.time()
            nextReConnectTime = conn.connectTime + self.reConnectIntervall
            if nextReConnectTime < now:
                # it's time to reconnect
                conn.reConnect()
                if self.logLevel:
                    log.log(self.logLevel,
                        "Reconnect connection %s" % self.serverPool.info)
            
        return conn

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.serverPool.info)


def getTestConnection(host='localhost', port='45200'):
    """Retruns a fresh connection which prevents to reuse an old one from
    another thread.
    """
    servers = ['%s:%s' % (host, port)]
    serverPool = ServerPool(servers) 
    conn = ElasticSearchConnection(serverPool)
    conn.close()
    return conn

##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
##############################################################################
"""tests
$Id:$
"""
__docformat__ = "reStructuredText"

import doctest
import httplib
import os.path
import time
import unittest

from p01.elasticsearch.pool import ServerPool
from p01.elasticsearch.pool import ElasticSearchConnectionPool
import p01.elasticsearch.connection
import p01.elasticstub.testing


###############################################################################
#
# sample data test setup
#
###############################################################################

# extract sample.zip data to sample/data
# sample/data <- source/sample.zip
def setUpSampleElasticSearch(test=None):
    esDir = os.path.join(os.path.dirname(__file__), 'sample')
    sandBoxDir = os.path.join(esDir, 'sandbox')
    confSource = os.path.join(esDir, 'config')
    dataSource = os.path.join(esDir, 'source', 'sample.zip')
    dataDir = os.path.join(esDir, 'data')
    p01.elasticstub.testing.startElasticSearchServer(sandBoxDir=sandBoxDir,
        dataSource=dataSource, dataDir=dataDir, confSource=confSource)

def tearDownSampleElasticSearch(test=None):
    p01.elasticstub.testing.stopElasticSearchServer()


# generate sample data and store as source/sample.zip
# sample/generator -> source/sample.zip
def setUpSampleGeneratorElasticSearch(test=None):
    esDir = os.path.join(os.path.dirname(__file__), 'sample')
    sandBoxDir = os.path.join(esDir, 'sandbox')
    confSource = os.path.join(esDir, 'config')
    dataDir = os.path.join(esDir, 'generator')
    p01.elasticstub.testing.startElasticSearchServer(sandBoxDir=sandBoxDir,
        dataDir=dataDir, confSource=confSource)

def tearDownSampleGeneratorElasticSearch(test=None):
    p01.elasticstub.testing.stopElasticSearchServer()


def setUpSampleData():
    """Setup sampledata method"""
    # start elasticsearch stub server
    setUpSampleGeneratorElasticSearch()

    # get es connection
    servers = ['localhost:45299']
    serverPool = ServerPool(servers, retryDelay=10,timeout=5)
    connectionPool = ElasticSearchConnectionPool(serverPool)
    conn = connectionPool.connection

    # setup indexes
    conn.createIndex('companies')

    # add some data
    for i in range(100):
        _id = unicode(i)
        doc = {'_id': _id,
               '__name__': u'name-%s' % _id,
               'street': u'street',
               'zip': u'zip',
               'city': u'city',
               'text': u'text',
               'number': i,
              }
        conn.index(doc, 'companies', 'company')

    # prepare teardown, this is what I really like to test. It seems that it
    # is really hard to do the sample generation tear down right because we
    # can't just stop eleasticsearch before all index are up to date.
    # flush translog
    conn.flush()
    # give some time to switch to green
    time.sleep(10)

    # stop elasticsearch stub server
    tearDownSampleGeneratorElasticSearch()

    # compress our elasticsearch sample data flder called "sample/generator"
    # and store them in source/sample.zip
    esDir = os.path.join(os.path.dirname(__file__), 'sample')
    folderPath = os.path.join(esDir, 'generator')
    zipPath = os.path.join(esDir, 'source', 'sample.zip')
    p01.elasticstub.testing.zipFolder(folderPath, zipPath)


def sampleSetUp(test):
    # run the elasticsearch server script which will setup our sample data
    # and zip them if finished. 
    # Note: normaly we call such a method as python script which will setup our
    # sample data. After that we sotre them in subversion or soemthing similar.
    # This will make the predefined sample data available out of the box for
    # the next test. If your sample data will change, just re-run the sample
    # generator script again and commit the new generated data to your source
    # control system.
    # We simply call this script here in the test setup beacuse we need a fully
    # automated test setup.
    setUpSampleData()
    # now setup our elasticsearch test server which will reuse the sample data
    setUpSampleElasticSearch()

def sampleTearDown(test):
    # stop our test server
    tearDownSampleElasticSearch()


###############################################################################
#
# simple test setup
#
###############################################################################

def doctestSetUp(test):
    # use default elasticsearch stub with our server dir
    here = os.path.dirname(__file__)
    sandBoxDir = os.path.join(here, 'sandbox')
    confSource = os.path.join(here, 'config')
    p01.elasticstub.testing.startElasticSearchServer(sandBoxDir=sandBoxDir,
        confSource=confSource)


def doctestTearDown(test):
    p01.elasticstub.testing.stopElasticSearchServer()


# tests
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('thrift.txt',
            setUp=doctestSetUp,
            tearDown=doctestTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        doctest.DocFileSuite('README.txt',
            setUp=doctestSetUp,
            tearDown=doctestTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        doctest.DocFileSuite('bulk.txt',
            setUp=doctestSetUp,
            tearDown=doctestTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        doctest.DocFileSuite('mapping.txt',
            setUp=doctestSetUp,
            tearDown=doctestTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        doctest.DocFileSuite('simple.txt',
            setUp=doctestSetUp,
            tearDown=doctestTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        doctest.DocFileSuite('scan.txt',
            setUp=doctestSetUp,
            tearDown=doctestTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        # sample data setup
        doctest.DocFileSuite('index.txt',
            setUp=sampleSetUp,
            tearDown=sampleTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        doctest.DocFileSuite('sample.txt',
            setUp=sampleSetUp,
            tearDown=sampleTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

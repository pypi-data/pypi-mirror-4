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

import json


class ElasticSearchException(Exception):
    pass

class ElasticSearchClientException(ElasticSearchException):
    pass

class NoServerAvailable(ElasticSearchClientException):
    pass

class InvalidQuery(ElasticSearchClientException):
    pass

class InvalidParameterQuery(InvalidQuery):
    pass

class QueryError(ElasticSearchClientException):
    pass

class QueryParameterError(ElasticSearchClientException):
    pass


class ElasticSearchServerException(ElasticSearchException):
    """An exception thrown by elasticsearch connection."""

    def __init__(self, error, status=None, reason=None, data=None):
        super(ElasticSearchServerException, self).__init__(error)
        self.status = status
        self.reason = reason
        self.data = data


class IndexMissingException(ElasticSearchServerException):
    pass

class NotFoundException(ElasticSearchServerException):
    pass

class IndexAlreadyExistsException(ElasticSearchServerException):
    pass

class SearchPhaseExecutionException(ElasticSearchServerException):
    pass

class ReplicationShardOperationFailedException(ElasticSearchServerException):
    pass

class ClusterBlockException(ElasticSearchServerException):
    pass


# Patterns used to map exception strings to classes.
EXCEPTIONS = {
    'IndexMissingException': IndexMissingException,
    'SearchPhaseExecutionException': SearchPhaseExecutionException,
    'ReplicationShardOperationFailedException': ReplicationShardOperationFailedException,
    'ClusterBlockException': ClusterBlockException,
}

WIRED_EXCEPTIONS = {
    'missing': NotFoundException,
    'IndexAlreadyExistsException': IndexAlreadyExistsException,
}

WIRED_EXCEPTION_MESSAGES = {
    'NotFoundException': 'missing',
    'IndexAlreadyExistsException': 'Already exists',
}


def checkResponse(response):
    """Raise an appropriate exception if the result is an error.

    Any result with a status code of 400 or higher is considered an error.

    The exception raised will either be an ElasticSearchServerException, or a
    more specific subclass of ElasticSearchServerException if the type is
    recognised.

    The status code and result can be retrieved from the exception by accessing
    its status and result properties.

    """
    status = response.status
    if status < 400:
        return response

    # everything else is raised as error
    reason = response.reason
    try:
        jsonStr = response.read()
        data = json.loads(jsonStr)
    except:
        data = {}

    if not isinstance(data, dict) or data.get('error') is None:
        raise ElasticSearchServerException("Unknown exception type", status,
            reason, data)

    error = data['error']
    bits = error.split('[', 1)
    if len(bits) == 2:
        excClass = EXCEPTIONS.get(bits[0], None)
        if excClass is not None:
            msg = bits[1]
            if msg.endswith(']'):
                msg = msg[:-1]
            raise excClass(msg, status, reason, data)

    for part, excClass in WIRED_EXCEPTIONS.items():
        if part in error:
            # get a nice error message
            msg = WIRED_EXCEPTION_MESSAGES.get(part, error)
            raise excClass(msg, status, reason, data)

    raise ElasticSearchServerException(error, status, reason, data)

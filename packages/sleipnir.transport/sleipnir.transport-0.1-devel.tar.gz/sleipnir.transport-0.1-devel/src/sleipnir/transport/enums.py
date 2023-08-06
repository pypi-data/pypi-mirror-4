#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
enums

Common enumerates used by transport modules
"""

from __future__ import absolute_import

__author__  = "Carlos Martin"
__license__ = "BSD, See LICENSE file for details"

# Import here any required modules.
import sleipnir.core

__all__ = [
    'ChannelTarget',
    'ChannelTargetState',
    'ConnectionState',
    'ConnectionType',
    'DeliveryMode',
    'RouteEndPosition',
    'RouteEndType',
    'RouteState',
    'RouteType',
    ]


class ChannelTarget(enum):
    ENTITY,    \
    ROUTE = xrange(0, 2)


class ChannelTargetState(enum):
    DECLARED,  \
    RESUMED,   \
    SUSPENDED, \
    DESTROYED = xrange(0, 4)


class ConnectionState(enum):
    UNKNOWN,   \
    CLOSED,    \
    STARTING,  \
    STARTED,   \
    CLOSING = xrange(0, 5)


class ConnectionType(enum):
    AUTO_ASYNC,     \
    AUTO_BLOCKING,  \
    AMQP_ASYNC,     \
    AMQP_BLOCKING,  \
    AMQP_MOCK,      \
    AMQP_TORNADO,   \
    HTTP_BLOCKING,  \
    HTTP_ASYNC = xrange(0, 8)


class DeliveryMode(enum):
    TRANSIENT, PERSISTENT = xrange(1, 3)


class RouteEndPosition(enum):
    ORIGIN,    \
    DESTINATION = xrange(0, 2)


class RouteEndType(enum):
    EXCHANGE,  \
    QUEUE = xrange(0, 2)


class RouteType(enum):
    EXCHANGE,  \
    QUEUE = xrange(2, 4)


class RouteState(enum):
    BIND,                  \
    UNBIND,                \
    DESTINATION_DECLARED,  \
    ORIGIN_DECLARED,       \
    UNKNOWN = xrange(0, 5)

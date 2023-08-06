#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Connections

Represents a generic gateway to AMQP implementation
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = ['ConnectionFactory']

# Project requirements
from sleipnir.core.factory import AbstractFactory
from sleipnir.core.decorators import deprecated

# local submodule requirements
from .enums import ConnectionType, ConnectionState
from .parser import connection_url, URI


class ConnectionError(Exception):
    """Connection exception"""


class ConnectionFactory(AbstractFactory):
    """Connection factory"""

    _shared_backends = {}
    _shared_connections = {}

    def __getattribute__(self, name):
        if name == '_backends':
            name = '_shared_backends'
        if name == '_connections':
            name = '_shared_connections'
        return object.__getattribute__(self, name)

    def __getitem__(self, key):
        return self._connections.get(key, None)

    def __delitem__(self, key):
        if key in self._connections:
            self._connections[key].close()
        del self._connections[key]

    def _on_connected(self, conn):
        conn.state = ConnectionState.STARTED
        if conn.url in self._connections:
            # invoke template method
            self.when_connected(conn)
            # add callbacks for close and backpressure events
            conn.add_on_close_callback(self._on_disconnected)
            conn.add_backpressure_callback(self._on_backpressure)

    def _on_disconnected(self, conn):
        conn.state = ConnectionState.CLOSED
        if conn.url in self._connections:
            self.when_disconnected(conn)

    def _on_backpressure(self, conn):
        if conn.url in self._connections:
            if not conn.push_timeout:
                conn.push_timeout = BACKPRESSURE
            conn.push_timeout *= BACKPRESSURE_MULTIPLIER
            conn.push_timeout = min(conn.push_timeout, BACKPRESSURE_LIMIT)
            # notify about pressure
            self.when_backpressure(conn)

    def _on_connection_timeout(self):
        for conn in self._connections.values():
            if conn.state == ConnectionState.STARTING:
                self.when_error(conn)
                del self._connections[conn.url]

    def when_connected(self, connection):
        pass

    def when_disconnected(self, connection):
        pass

    def when_backpressure(self, connection):
        pass

    def when_error(self, connection):
        pass

    def create(self, url, conn_type=ConnectionType.AUTO_ASYNC):
        # check that url pased (url_string, connection or channel)
        # doesn't exist in connections pool
        connection = url
        if hasattr(connection, 'slp_connection'):
            connection = url.slp_connection
        if isinstance(connection, AbstractConnection):
            url = connection.url

        # handle auto case
        if conn_type == ConnectionType.AUTO_ASYNC:
            if url.startswith("amqp"):
                conn_type = ConnectionType.AMQP_ASYNC
            elif url.startswith("http"):
                conn_type = ConnectionType.HTTP_ASYNC
            else:
                raise NotImplementedError
            
        # check now url
        if url not in self._connections:
            conn = super(ConnectionFactory, self).create(url, conn_type)
            self._connections[url] = conn
            # set callbacks
            conn.add_on_open_callback(self._on_connected)
            # add a timeout so if connection isn't valid, we should remove it
            conn.add_timeout(2, self._on_connection_timeout)
            conn.state = ConnectionState.STARTING
        return self._connections[url]


class MetaConnection(type):
    """Connection Metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if not name.endswith("Connection"):
            ConnectionFactory.get_instance().register(name, mcs)


class AbstractConnection(object):
    """Prepares a connection. only get a pika connection is lazy created"""

    __metaclass__ = MetaConnection

    def __init__(self, url, limit=4):
        """Whenever a property changes, update stamp"""
        self._url = URI(url, connection_url)
        self._state = ConnectionState.CLOSED

    @property
    def type(self):
        return self.CONNECTION_TYPE

    @property
    def url(self):
        return str(self._url)

    @property
    def loop(self):
        raise NotImplementedError

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @classmethod
    def can_handle(cls, url, conn_type):
        return cls.CONNECTION_TYPE == conn_type

    @classmethod
    def new(cls, url, conn_type):
        return cls(url)

# load connection implementations
from .amqp.connections import *
from .http.connections import *

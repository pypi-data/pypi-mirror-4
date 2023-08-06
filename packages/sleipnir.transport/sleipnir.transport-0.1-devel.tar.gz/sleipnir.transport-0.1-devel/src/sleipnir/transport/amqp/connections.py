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
from pika import PlainCredentials, ConnectionParameters
from pika.adapters import SelectConnection

__all__ = []

# Project requirements

# local submodule requirements
from ..enums import ConnectionType
from ..connections import AbstractConnection
from .pools import ChannelPool, BuilderPool

BACKPRESSURE = 0.15
BACKPRESSURE_LIMIT = 90
BACKPRESSURE_MULTIPLIER = 3


class AMQPConnection(AbstractConnection):
    """Prepares a connection. only get a pika connection is lazy created"""

    def __init__(self, url, limit=4):
        """Whenever a property changes, update stamp"""
        AbstractConnection.__init__(self, url)
        # AMQP backpressure
        self._push_timeout = 0
        # set up pools
        self._builders_pool = BuilderPool(self)
        self._channels_pool = ChannelPool(self, limit)

    @property
    def channels(self):
        return self._channels_pool

    @property
    def builders(self):
        return self._builders_pool

    @property
    def loop(self):
        # get connection variable to be used by start method
        connection = self

        def start(self, timeout=None):
            if timeout is not None:
                connection.add_timeout(timeout, connection.close)
            return self.__class__.start(self)

        # Start event loop
        if not hasattr(self.ioloop, "slp_monkey_patched"):
            self.ioloop.slp_monkey_patched = True
            klass = self.ioloop.__class__
            func_type = type(klass.start)
            self.ioloop.start = func_type(start, self.ioloop, klass)
        return self.ioloop

    @property
    def push_timeout(self):
        return self._push_timeout

    @push_timeout.setter
    def push_timeout(self, value):
        self._push_timeout = value

    def routes(self, builder, **builder_kwargs):
        builder = builder(self, **builder_kwargs)
        return self._builders_pool.register(builder)


class ConnectionMockAMQP(AMQPConnection):
    """A mock connection object"""

    CONNECTION_TYPE = ConnectionType.AMQP_MOCK

    class IOLoopMock(object):
        def start(self):
            pass

    @property
    def loop(self):
        return IOLoopMock()


class PikaConnection(AMQPConnection):

    def __init__(self, url):
        AMQPConnection.__init__(self, url)

        credentials = None
        if self._url.username:
            credentials = PlainCredentials(
                self._url.username, self._url.password)

        for host, port in self._url.hosts():
            self._parameters = ConnectionParameters(
                credentials=credentials,
                host=host,
                port=port,
                virtual_host=self._url.vhost)

            #Fixme: Support multiple hosts
            break


class ConnectionAMQP(PikaConnection, SelectConnection):

    CONNECTION_TYPE = ConnectionType.AMQP_ASYNC

    def __init__(self, url):
        PikaConnection.__init__(self, url)
        SelectConnection.__init__(self, self._parameters)

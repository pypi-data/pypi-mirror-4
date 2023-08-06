#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Routers

Base classes to implement message routing patters (EIP2003)
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = ['Routers']

# Project requirements

REPLY_TO = "reply_to"

# local submodule requirements
from .endpoints import EndPoint
from ..connections import ConnectionFactory
from ..amqp.channels import ChannelEnd, Consumer, Producer


class Relay(object):

    # replay factory option
    producer = Producer
    producer_opt = {}

    def __init__(self, callback):
        # init connection stuff
        self._callback = callback
        self._routing = {}

    def __getattr__(self, value):
        return getattr(self._routing, value)

    def replay(self, message, properties, receivers=None):
        rcvs = receivers if receivers is not None else self._routing.iterkeys()
        for recipient in rcvs:
            producer = self._routing[recipient][1]
            producer.publish(producer.prepare(message, **properties))

    def add_route(self, route, contents):
        # remove replayer if a empty message is send
        if route in self._routing and len(contents) == 0:
            del self._routing[route]
            return
        # otherwise create producer and and to routes
        publisher = self._callback(
            route,
            self.producer,
            self.producer_opt)
        self._routing[route] = (contents, publisher,)


class EndPointRelay(EndPoint):

    # control queue options
    control = Consumer
    control_opt = {}

    def __init__(self, request=None, control=None,
                 error=None, connection=None, factory=ChannelEnd.create):

        # init consumer and setup callbacks
        super(EndPointRelay, self).__init__(request, None, error, connection)
        # set up relay
        self._relay = Relay(lambda x, y, z: factory(x, y, z, connection))
        # setup control and relay compose
        self._control = ChannelEnd.create(
            control,
            self.control,
            self.control_opt,
            connection)
        self._control  and self._control.append_callbacks(self.process_control)
        self._consumer and self._consumer.append_callbacks(self.process)

    def __getattr__(self, value):
        return getattr(self._relay, value)

    def run(self, timeout=None):
        self._control.consume(timeout)
        super(EndPointRelay, self).run(timeout)

    def process(self, request, response, receivers=None):
        self._relay.replay(request, response, receivers)

    def process_control(self, request, message):
        route = message.properties[REPLY_TO]
        if route is not None:
            self._relay.add_route(route, message.payload)

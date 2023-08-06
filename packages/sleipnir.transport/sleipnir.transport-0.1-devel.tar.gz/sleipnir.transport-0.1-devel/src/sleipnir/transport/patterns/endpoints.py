#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
EndPoints

Base classes to implement message endpoints (EIP2003)
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from functools import partial

__all__ = ['Endpoint', 'Replier', 'Requestor', 'Replay']

# Project requirements
from sleipnir.core.decorators import cached
from sleipnir.core.utils import maybe_list, uuid

# local submodule requirements
from ..connections import ConnectionFactory
from ..amqp.channels import Producer, Consumer, ChannelEnd

RELAY = 'relay'
REPLY_TO = 'reply_to'
MESSAGE_ID = 'message_id'
CORRELATION_ID = 'correlation_id'


class EndPoint(object):

    # default consumer options to be used
    # when a new Consumer is created
    consumer = Consumer
    consumer_opt = {}

    # default consumer options to be used
    # when a new Producer is created
    producer = Producer
    producer_opt = {}

    # invalid exchange options
    invalid = None
    invalid_opt = {}

    def __init__(self, request, reply=None, error=None, connection=None):
        #setup connection
        factory = ConnectionFactory.get_instance()
        self._connection = conn = factory.create(connection)

        #create routes
        factory = ChannelEnd.create
        error = factory(error, self.invalid, self.invalid_opt, conn)
        consumer = factory(request, self.consumer, self.consumer_opt, conn)
        producer = factory(reply, self.producer, self.producer_opt, conn)
        # store routes
        self._error, self._consumer, self._producer = error, consumer, producer

    def reply(self, response, message, reply=None):
        reply = reply or self._producer or self._error
        reply and reply.publish((response, message,))

    def run(self, timeout=None):
        self._consumer.consume(timeout) if self._consumer else None

    @property
    @cached
    def nodes(self):
        class Ends(object):
            def __init__(self, producer, consumer, error):
                self.consumer = consumer
                self.producer = producer
                self.error = error
        return Ends(self._producer, self._consumer, self._error)


class _Wrapper(object):
    def __init__(self, callback=None):
        self._callback = callback

    def __getattr__(self, value):
        return partial(self.__invoke, value)

    def __invoke(self, method, *args, **kwargs):
        method = getattr(self._callback, method, None)
        return method(*args, **kwargs) if method else args[0]


class Replier(EndPoint):

    def __init__(self, request, error=None, connection=None, callback=None):
        super(Replier, self).__init__(request, None, error, connection)
        self._repliers = {}
        self._callback = _Wrapper(callback)
        self._consumer.append_callbacks(self.process)

    def _get_replier(self, address):
        if address not in self._repliers:
            exchange = address if '@' in address else '@' + address
            self._repliers[address] = ChannelEnd.create(
                exchange,
                self.producer,
                self.producer_opt,
                self._connection)
        # get valid replier
        return self._repliers[address]

    def process(self, request, message):
        # fetch data
        payload, props = message.payload, message.properties
        reply_to, message_id = props[REPLY_TO], props[MESSAGE_ID]
        # send to replier
        payload, props = self._callback.process(payload, props)
        if reply_to is not None:
            # publish in replier
            props.setdefault(MESSAGE_ID, uuid())
            props.setdefault(CORRELATION_ID, message_id)
            replier = self._get_replier(reply_to)
            # prepare message
            message = replier.prepare(payload, **props)
            message = self._callback.prepared(message)
            # publish reply
            replier.publish(message)
            self._callback.published(message)


class Requestor(EndPoint):
    def __init__(self, request, response,
                 error=None, connection=None, callback=None):
        super(Requestor, self).__init__(request, response, error, connection)
        self._callback = _Wrapper(callback)
        self._consumer.append_callbacks(self._callback.response)

    def request(self, request=None, headers={}):
        requests = self._callback.request(request, headers)
        messages = requests if hasattr(requests, 'next') else [requests]
        # publish request
        for request, headers in messages:
            message = self._producer.prepare(request, **headers)
            message = self._callback.prepared(message)
            self._producer.publish(message)
            self._callback.published(request, message)

    def run(self, timeout=None):
        self._producer.pending += [
            self.request,
            partial(super(Requestor, self).run, timeout),
        ]


class Replay(EndPoint):
    def __init__(self, request, reply=None, error=None, connection=None):
        self.consumer_opts[RELAY] = True
        super(Replay, self).__init__(request, None, error, connection)

    def process(self, request, message):
        self.reply(request, message)


class Manager(object):
    def __init__(self, endpoints=None):
        self._processes = {}
        self._producers = {}
        self._consumers = {}
        # store active processes here
        for end in maybe_list(endpoints):
            if hasattr(end, 'consume'):
                callback = partial(self.process, end)
                end.append_callbacks(callback)
                self._consumers[end.queues[0]] = end
            if hasattr(end, 'publish'):
                self._producers[end.exchange] = end

    def __getattr__(self, value):
        return getattr(self._processes, value)

    def when_process_completed(self, process_key):
        del self._processes[process_key]

    def run(self, timeout=None):
        [cons.consume(timeout) for cons in self._consumers.itervalues()]

    def process(self, end, request, message):
        raise NotImplementedError

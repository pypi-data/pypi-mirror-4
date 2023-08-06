#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Channel

Producer/Consumer entities
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from functools import partial
from itertools import ifilter
from pika import BasicProperties

__all__ = ['Producer', 'Consumer']

# Project requirements
from sleipnir.core.utils import maybe_list, uuid
from sleipnir.core.async import engine, Task

# local submodule requirements
from ..enums import ChannelTarget, ChannelTargetState, DeliveryMode
from ..connections import ConnectionFactory
from ..serialization import encode
from ..compression import compress
from .connections import BACKPRESSURE, BACKPRESSURE_MULTIPLIER
from .messaging import Message


class ChannelEnd(object):

    def __init__(self, routes, connection=None):
        def __acquire_callback(connection):
            connection.channels.acquire(self._constructed)

        # fetch connection. Create a default one if required
        if not connection or type(connection) in (str, unicode):
            pool = ConnectionFactory.get_instance()
            conn = pool.create(connection) if connection else pool.default
            connection = conn

        # define watch containers, indexed by watcher id and also
        # indexed by group familiarity. This is required to be able to
        # implement the first (any) case
        self._watchers = []

        # now set variables
        self._routes = maybe_list(routes)

        # store connection temporarily into channel var so empty watch
        # calls works
        self._channel = connection.channels.default or connection

        # pending queue. Store here any early call to method when
        # channel isn't set properly yet
        self._pending = []

        # open a chanel if no one is available for this thread
        # wait till a channel is available for this connection
        if not connection.channels.default:
            connection.add_on_open_callback(__acquire_callback)

    def _constructed(self, channel):
        self._channel = channel
        # if watchers is empty, we assume that routes are up and
        # running so, we start to listen
        if not self._watchers:
            self.when_resumed(None, None)

    def watch(self, builders=None, target=ChannelTarget.ROUTE,
              state=ChannelTargetState.RESUMED, first=True):

        pool = ConnectionFactory.get_instance().create(self._channel).builders
        wwid = pool.add_entity_watch(self, builders, target, state, first)
        self._watchers.append(wwid)
        return wwid

    def unwatch(self, wgid=[]):
        pool = ConnectionFactory.get_instance().create(self._channel).builders
        for wwid in maybe_list(wgid) or self._watchers:
            if wwid in self._watchers:
                pool.remove_watch(wwid)
                self._watchers.remove(wwid)

    @property
    def routes(self):
        return self._routes

    @property
    def pending(self):
        return self._pending

    @pending.setter
    def pending(self, value):
        self._pending = maybe_list(value)

    def when_declared(self, channel_end, frame):
        pass

    def when_destroyed(self):
        pass

    def when_resumed(self, route, frame):
        [pending() for pending in self._pending]

    def when_suspended(self):
        pass

    @staticmethod
    def create(name, creator, options={}, connection=None):
        channel_end = name
        if type(channel_end) in (str, unicode,):
            conn = ConnectionFactory.get_instance().create(connection)
            # used for exchanges
            node, _, routing_key = name.partition('@')
            # set routing key
            roptions = options
            if routing_key:
                roptions = dict(options)
                roptions.setdefault('routing_key', routing_key)
            channel_end = creator(node, conn, **roptions)
        return channel_end


class Producer(ChannelEnd):

    def __init__(self, routes, connection=None, routing_key="",
                 serializer=None, compression=None):

        # Call parent
        super(Producer, self).__init__(routes, connection)

        # init internal elements
        self._routing_key = routing_key
        self._serializer = serializer
        self._compression = compression

    def _encode_payload(self, body, serializer=None, content_type=None,
                        content_encoding=None):

        # No content_type? Then we're serializing the data internally.
        if not content_type:
            serializer = serializer or self._serializer
            (content_type, content_encoding, body) = encode(body, serializer)
        else:
            # If the programmer doesn't want us to serialize,
            # make sure content_encoding is set.
            if isinstance(body, unicode):
                content_encoding = content_encoding or 'utf-8'
                body = body.encode(content_encoding)
            # If they passed in a string, we can't know anything
            # about it. So assume it's binary data.
            content_encoding = content_encoding or 'binary'

        # return formatted message
        return body, content_type, content_encoding

    def _compress_payload(self, body, compression=None, headers=None):
        if compression is None:
            # Allow compression = 'empty' string to force uncompress
            # when compress is enabled by default
            compression = self._compression
        if compression:
            body, headers["compression"] = compress(body, compression)
        return body

    def prepare(self, body, routing_key=None, mandatory=False, immediate=False,
                content_type=None, content_encoding=None, serializer=None,
                compression=None, headers=None,
                delivery_mode=DeliveryMode.PERSISTENT,
                **properties):

        # serialize payload
        args = (body, serializer, content_type, content_encoding)
        body, content_type, content_encoding = self._encode_payload(*args)

        # compress payload
        headers = headers or {}
        body = self._compress_payload(body, compression, headers)

        # prepare envelope
        exchange = self.exchange
        routing_key = routing_key or self._routing_key
        properties = BasicProperties(
            content_type=content_type,
            content_encoding=content_encoding,
            delivery_mode=int(delivery_mode),
            headers=headers,
            **properties)

        # return message
        return (exchange, routing_key, body, properties, mandatory, immediate,)

    @engine
    def delay_publish(self, message, callback, timeout=None):
        # wait required?
        connect = self._channel.slp_connection
        timeout = timeout if timeout is not None else connect.push_timeout
        if timeout > 0:
            yield Task(connect.add_timeout, timeout)
        #invoke
        self.publish(message)
        callback(message)
        # reset backpressure counter?
        if timeout:
            new_timeout = connect.push_timeout
            if timeout == connect.push_timeout:
                new_timeout /= BACKPRESSURE_MULTIPLIER
            if new_timeout <= BACKPRESSURE:
                new_timeout = 0
            connect.push_timeout = new_timeout

    def publish(self, message):
        if not hasattr(self._channel, "slp_connection"):
            pending = partial(self.publish, message)
            self._pending.append(pending)
            return
        if type(message) not in (list, tuple,):
            message = tuple(self.prepare(message))
        #publish message
        self._channel.basic_publish(*message)

    @property
    def exchange(self):
        return self._routes[0] if self._routes else ""

    @property
    def routing_key(self):
        return self._routing_key

    @property
    def serializer(self):
        return self._serializer

    @property
    def compression(self):
        return self._compression


class Consumer(ChannelEnd):
    def __init__(self, routes, connection=None, no_ack=True,
                 exclusive=False, relay=False, callbacks=[],
                 on_decode_error=None):

        # init internal elements
        self._relay = relay
        self._no_ack = no_ack
        self._exclusive = exclusive
        self._callbacks = list(maybe_list(callbacks))
        self._on_decode_error = on_decode_error
        self._active_tags = {}

        # Call parent
        super(Consumer, self).__init__(routes, connection)

    def __iadd__(self, queues):
        self._routes += maybe_list(queues)
        raise NotImplementedError

    def __idel__(self, queues):
        for queue in maybe_list(queues):
            self._routes.remove(queue)

    def _receive(self, *args):
        try:
            message = Message(self._channel, args)
            decoded = message.payload if not self._relay else None
        except Exception, ex:
            if self._on_decode_error:
                self._on_decode_error(message, ex)
                return
            raise
        else:
            self.when_received(decoded, message)

    def append_callbacks(self, callbacks):
        self._callbacks += maybe_list(callbacks)

    def remove_callbacks(self, callbacks):
        for callback in maybe_list(callbacks):
            self._callbacks.remove(callback)

    def consume(self, no_ack=None, exclusive=None, timeout=None):
        if not hasattr(self._channel, "slp_connection"):
            pending = partial(self.consume, no_ack, exclusive, timeout)
            self._pending.append(pending)
            return

        no_ack = no_ack or self._no_ack
        exclus = exclusive or self._exclusive

        tags = []
        queue_filter = lambda x: x not in self._active_tags.itervalues()

        for queue in ifilter(queue_filter, self._routes):
            channel = self._channel
            tag = channel.basic_consume(self._receive, queue, no_ack, exclus)
            self._active_tags[tag] = queue
            tags.append(tag)
            no_ack and channel.slp_no_ack_consumers.append(tag)
        if timeout:
            timeout_callback = partial(self.cancel, tags=tags)
            self._channel.slp_connection.add_timeout(timeout, self.cancel)

        # notify consume
        self.when_consumed(tags)
        return tags

    def cancel(self, queues=None, tags=None):
        # lookup for valid tags
        tags = tags or []
        queues = queues or []
        [tags.append(tag) for tag, queue      \
             in self._active_tags.iteritems() \
             if queue in queues]

        # no tags? use all active consumers or queues pased
        tags = tags or self._active_tags.keys()
        # cancel selected consumers
        for tag in tags:
            self._channel.basic_cancel(self._active_tags.pop(tag))
            if tag in self._channel.slp_no_ack_consumers:
                self._channel.slp_no_ack_consumers.remove(tag)
        # notify cancellation
        self.when_canceled(tags)

    def when_received(self, body, message):
        if message.delivery_info['consumer_tag'] in self._active_tags:
            [callback(body, message) for callback in self._callbacks]

    def when_consumed(self, tags):
        pass

    def when_canceled(self, tags):
        pass

    @property
    def queues(self):
        return self._routes

    @property
    def consumer_tags(self):
        return self._active_tags.iteritems()

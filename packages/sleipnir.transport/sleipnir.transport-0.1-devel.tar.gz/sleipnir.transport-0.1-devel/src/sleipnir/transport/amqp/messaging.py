#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Messaging

A wrapper around AMQP frames
"""

from __future__ import absolute_import

__author__  = "Ask Solem"
__license__ = "BSD like LICENSE"

# Import here any required modules.
from operator import attrgetter

# Inport local requirements
from ..compression import decompress
from ..serialization import decode
from ..errors import MessageStateError


class AbstractMessage(object):
    """Base class for received messages."""

    ACKNOWLEDGED_STATES = frozenset([
            "ACK", "ACK_MULTIPLE", "REJECTED", "REQUEUED"
    ])

    _state = None

    MessageStateError = MessageStateError

    #: The channel the message was received on.
    channel = None

    #: Delivery tag used to identify the message in this channel.
    delivery_tag = None

    #: Content type used to identify the type of content.
    content_type = None

    #: Content encoding used to identify the text encoding of the body.
    content_encoding = None

    #: Additional delivery information.
    delivery_info = None

    #: Message headers
    headers = None

    #: Application properties
    properties = None

    #: Raw message body (may be serialized), see :attr:`payload` instead.
    body = None

    def __init__(self, channel, body=None, delivery_tag=None,
                 content_type=None, content_encoding=None, delivery_info={},
                 properties=None, headers=None, postencode=None,
                 **kwargs):

        self.channel = channel
        self.body = body
        self.delivery_tag = delivery_tag
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.delivery_info = delivery_info
        self.headers = headers or {}
        self.properties = properties or {}

        compression = self.headers.get("compression")
        if compression:
            self.body = decompress(self.body, compression)
        if postencode and isinstance(self.body, unicode):
            self.body = self.body.encode(postencode)

        self._decoded_cache = None
        self._state = "RECEIVED"

    def ack(self, multiple=False):
        """Acknowledge this message as being processed.,
        This will remove the message from the queue.

        :raises MessageStateError: If the message has already been
            acknowledged/requeued/rejected.

        """
        if self.acknowledged:
            msg = "Message already acknowledged with state: %s" % self._state
            raise self.MessageStateError(msg)
        # confirm
        if self.channel.slp_no_ack_consumers:
            no_ack_list = self.channel.slp_no_ack_consumers
            if self.delivery_info.get("consumer_tag") in no_ack_list:
                return
        # set ACK_MULTIPLE for all previous messages
        if multiple:
            self.channel.slp_last_ack_deliver = self.delivery_tag
        # send ACK
        self.channel.basic_ack(self.delivery_tag, multiple)
        self._state = "ACK"

    def reject(self):
        """
        Reject this message.

        The message will be discarded by the server.

        :raises MessageStateError: If the message has already been
            acknowledged/requeued/rejected.
        """
        if self.acknowledged:
            msg = "Message already acknowledged with state: %s" % self._state
            raise self.MessageStateError(msg)
        # reject message
        self.channel.basic_reject(self.delivery_tag, requeue=False)
        self._state = "REJECTED"

    def requeue(self):
        """
        Reject this message and put it back on the queue.

        You must not use this method as a means of selecting messages
        to process.

        :raises MessageStateError: If the message has already been
            acknowledged/requeued/rejected.
        """
        if self.acknowledged:
            msg = "Message already acknowledged with state: %s" % self._state
            raise self.MessageStateError(msg)
        # requeue message
        self.channel.basic_reject(self.delivery_tag, requeue=True)
        self._state = "REQUEUED"

    def decode(self):
        """
        Deserialize the message body, returning the original python
        structure sent by the publisher.
        """
        return decode(self.body, self.content_type, self.content_encoding)

    @property
    def acknowledged(self):
        """Set to true if the message has been acknowledged."""

        if self._state in self.ACKNOWLEDGED_STATES:
            return True

        last_deliver = self.channel.slp_last_ack_deliver
        if last_deliver and last_deliver > self.delivery_tag:
            self._state = "ACK_MULTIPLE"
            return True

        # no acknowledge
        return False

    @property
    def payload(self):
        """The decoded message body."""
        if not self._decoded_cache:
            self._decoded_cache = self.decode()
        return self._decoded_cache


class Message(AbstractMessage):

    PROPERTIES = (
        "app_id",
        "cluster_id",
        "content_encoding",
        "content_type",
        "correlation_id",
        "delivery_mode",
        "expiration",
        "headers",
        "message_id",
        "priority",
        "reply_to",
        "timestamp",
        "type",
        "user_id",
        )

    def __init__(self, channel, frame, **kwargs):
        channel_id, method, props, body = frame

        # prepare kwargs
        dinfo = dict(
            consumer_tag=getattr(method, "consumer_tag", None),
            routing_key=method.routing_key,
            delivery_tag=method.delivery_tag,
            redelivered=method.redelivered,
            exchange=method.exchange)
        attrs = dict(zip(self.PROPERTIES, attrgetter(*self.PROPERTIES)(props)))

        # update
        kwargs.update({
                "body":             body,
                "delivery_tag":     method.delivery_tag,
                "content_type":     props.content_type,
                "content_encoding": props.content_encoding,
                "headers":          props.headers,
                "properties":       attrs,
                "delivery_info":    dinfo,
                })

        super(Message, self).__init__(channel, **kwargs)

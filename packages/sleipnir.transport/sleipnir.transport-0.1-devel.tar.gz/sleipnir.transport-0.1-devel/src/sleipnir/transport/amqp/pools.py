#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Pools

Represents a generic gateway to AMQP implementation
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from Queue import Queue, Empty
from thread import get_ident
from threading import Lock
from functools import partial

__all__ = ['BuilderPool', 'ChannelPool']

# Project requirements
from sleipnir.core.utils import uuid, maybe_list

# local requirements
from ..errors import ConnectionError


class BuilderPool(object):
    def __init__(self, connection):
        self.__connection = connection
        self._builders = {}
        self._entities = {}
        self._watchers = {}

    def register(self, builder):
        # set default values
        self._builders.setdefault(get_ident(), []).append(builder)
        self._entities.setdefault(get_ident(), {})
        # add watch
        for entity, values in self._entities[get_ident()].iteritems():
            self.add_entity_watch(entity, builder, **values)
        return builder

    def add_entity_watch(self, entity, builders, target, state, first):
        wbls, wgid = [], uuid()

        # get a list/tuple of builders
        pool = maybe_list(builders) or self._builders.get(get_ident(), [])
        if type(pool) not in (list, tuple,):
            pool = [pool]
        # create watchers
        for builder in pool:
            wid = builder.add_entity_watch(entity, target, state)
            self._watchers.setdefault(wgid, wbls).append((wid, builder,))
        # store params to listen to new declared builders
        if builders is None:
            kwargs = {'target': target, 'state': state, 'first': first}
            self._entities.setdefault(get_ident(), {})
            self._entities[get_ident()][entity] = kwargs
        return wgid

    def __iter__(self):
        return iter(self._builders.get(get_ident(), []))


class ChannelPool(object):
    def __init__(self, connection, limit):
        self._limit = limit
        self._cconn = connection
        self._queue = Queue(self._limit)
        self._qlock = Lock()
        self._cpool = {}

        # channel callbacks
        self._close = {}
        self._error = {}

    def __iter__(self):
        return self._cpool.itervalues()

    def __getattr__(self, name):
        getattr(self._cpool, name)

    def _close_channel(self, channel, code, text):
        callbacks = self._close.get(get_ident(), [])
        [callback(code, text) for callback in callbacks]
        # now remove channel from available channels. Becose channel
        # it's closed, it won't be available anymore
        self.release(channel)
        if self._queue.empty() and code != 200 and not callbacks:
            raise ConnectionError(code, text)

    def _error_channel(self, channel, frame, message):
        callbacks = self._error.get(get_ident(), [])
        [callback(frame, message) for callback in callbacks]

    def _consume_channel(self):
        # block until a channel is available
        try:
            for thread, callbacks in self._cpool.iteritems():
                if type(callbacks) in (list, tuple):
                    channel = self._queue.get(False)
                    self._cpool[thread] = channel
                    [callback(channel) for callback in callbacks]
                    return
            else:
                raise ConnectionError("Orphan channel")
        except Empty:
            pass

    def _produce_channel(self, channel):
        # Add custom properties
        channel.slp_connection = self._cconn
        channel.slp_last_ack_deliver = None
        channel.slp_no_ack_consumers = []
        channel.add_on_close_callback(partial(self._close_channel, channel))
        channel.add_on_return_callback(partial(self._error_channel, channel))

        self._queue.put(channel)
        self._consume_channel()

    def _release_channel(self, ident):
        channel = self._cpool[ident]
        assert channel and type(channel) not in (list, tuple)
        del self._cpool[ident]
        if not channel.closing:
            self._queue.put(channel)
            self._queue.task_done()
            self._consume_channel()

    def acquire(self, callback):
        # shortcut to get assigned channel
        thread = get_ident()
        channel = self._cpool.setdefault(thread, [])
        if type(channel) not in (list, tuple):
            callback(channel)
            return

        # register callback
        assert callback not in self._cpool
        self._cpool[thread].append(callback)

        # produce channel if required
        self._qlock.acquire()
        if (len(self._cpool) - 1) + self._queue.qsize() < self._limit:
            if len(self._cpool[thread]) == 1:
                self._cconn.channel(self._produce_channel)
        self._qlock.release()

    def release(self, channel=None):
        channel = channel or self._cpool[get_ident()]
        for key, values in self._cpool.iteritems():
            if values == channel:
                self._release_channel(key)
                break

    @property
    def default(self):
        retval = self._cpool.get(get_ident(), None)
        return retval if type(retval) not in (list, tuple) else None

    @property
    def closes(self):
        return self._closes.setdefault(get_ident(), [])

    @property
    def returns(self):
        return self._return.setdefault(get_ident(), [])

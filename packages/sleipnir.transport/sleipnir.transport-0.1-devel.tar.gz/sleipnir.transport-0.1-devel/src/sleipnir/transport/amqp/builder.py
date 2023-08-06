#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
builder

Represents a generic gateway to AMQP implementation
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from functools import partial
from itertools import ifilter

__all__ = ['Builder']

# Project requirements
from sleipnir.core.factory import AbstractFactory
from sleipnir.core.utils import maybe_list, uuid
from sleipnir.core.async import Task, engine

# local submodule requirements
from ..enums import ChannelTargetState, ChannelTarget, RouteState
from ..enums import RouteEndType, RouteType, RouteState
from .routes import Route


class BrokerFactory(AbstractFactory):
    """Broker private"""


class MetaBroker(type):
    """Broker Metaclass"""
    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if name.endswith("Broker"):
            mcs.__merge(mcs.mro())
            BrokerFactory.get_instance().register(name, mcs)

    def __merge(mcs, mro):
        if 'attrs' in dir(mcs):
            mro_filter = lambda x: mcs != x and 'attrs' in dir(x)
            for pcs in ifilter(mro_filter, mro):
                new_attrs = pcs.attrs.copy()
                for key, value in mcs.attrs.iteritems():
                    new_attrs.setdefault(key, {}).update(value)
                mcs.attrs = new_attrs


class BrokerAbstract(object):

    __metaclass__ = MetaBroker

    attrs = {
        RouteEndType.EXCHANGE: {
            'type':               ('type',        None, None),
            'passive':            ('passive',     bool, None),
            'durable':            ('durable',     bool, None),
            'auto-delete':        ('auto-delete', bool, None),
            'internal':           ('internal',    bool, None),
            'no-wait':            ('no-wait',     bool, None),
            },
        RouteEndType.QUEUE: {
            'passive':            ('passive',     bool, None),
            'durable':            ('durable',     bool, None),
            'auto-delete':        ('auto-delete', bool, None),
            'exclusive':          ('exclusive',   bool, None),
            'no-wait':            ('no-wait',     bool, None),
            },
        RouteType.QUEUE: {
            'origin':             ('exchange',    None, None),
            'destination':        ('queue',       None, None),
            'no-wait':            ('no-wait',     None, None),
            'routing-key':        ('routing-key', None, None),
            }
        }

    def create_entity(self, entity, callback=None):
        raise NotImplementedError

    def delete_entity(self, entity, callback=None):
        raise NotImplementedError

    def resume_route(self, route, callback=None):
        raise NotImplementedError

    def suspend_route(self, route, callback=None):
        raise NotImplementedError


class PikaScaffoldBroker(BrokerAbstract):
    """Simple broker"""

    def _type(value):
        extension = "-exchange"
        return value[:len(extension)] if value.endswith(extension) else value

    attrs = {
        RouteEndType.EXCHANGE: {
            'destination':        ('exchange',    None,  None),
            'origin':             ('exchange',    None,  None),
            'type':               ('type',        _type, False),
            'auto-delete':        ('auto_delete', bool,  None),
            'no-wait':            ('nowait',      bool,  None),
            # extra parameters
            'alternate-exchange': ('alternate-exchange', None, 'params')
            },
        RouteEndType.QUEUE: {
            'destination':        ('queue',       None,  None),
            'auto-delete':        ('auto_delete', bool,  None),
            'no-wait':            ('nowait',      bool,  None),
            },
        RouteType.QUEUE: {
            'no-wait':            ('nowait',      bool,  None),
            'routing-key':        ('routing_key', None,  None),
            }
        }

    @classmethod
    def can_handle(cls, connection, **kwargs):
        url = connection.url
        return url.startswith('amqp:') and not kwargs.get("force", False)


class PikaBroker(PikaScaffoldBroker):
    """defines primitves to build routes"""

    def __init__(self, connection, **kwargs):
        self._connection = connection

    @engine
    def create_entity(self, entity, callbacks):
        # peek thread channel
        channel = self._connection.channels.default
        # declare entities
        if entity.end_type == RouteEndType.EXCHANGE:
            if entity.name and not entity.name.startswith('amq'):
                frame = yield Task(channel.exchange_declare, **entity.params)
                [callback(entity, frame) for callback in callbacks]
        if entity.end_type == RouteEndType.QUEUE:
            frame = yield Task(channel.queue_declare, **entity.params)
            [callback(entity, frame) for callback in callbacks]

    @engine
    def resume_route(self, route, callbacks):
        # peek thread channel
        channel = self._connection.channels.default
        rparams = route.params(self.attrs)
        # don't bind if we are using a default exchange
        if not route.origin.name:
            [callback(route, None) for callback in callbacks]
            return
        # bind routes
        if route.route_type == RouteType.QUEUE:
            frame = yield Task(channel.queue_bind, **rparams)
            [callback(route, frame) for callback in callbacks]
        if route.route_type == RouteType.EXCHANGE:
            frame = yield Task(channel.exchange_bind, **rparams)
            [callback(route, frame) for callback in callbacks]

    @classmethod
    def can_handle(cls, connection, **kwargs):
        url = connection.url
        return url.startswith('amqp:')    \
            if kwargs.get("force", False) \
            else url.startswith('amqp-dev:')


class MockBroker(BrokerAbstract):
    @classmethod
    def can_handle(cls, url, **kwargs):
        url = connection.url
        return url.startswith('mock:')


class Builder(object):

    class RouteBuilder(object):

        def __init__(self, route, builder):
            self._route = route if isinstance(route, Route) else Route(route)
            self._build = builder

        def create(self, callback=None):
            broker = self._build._broker
            brokcb = maybe_list(callback)
            brokcb.append(self._build.when_created)

            # don't declare again if already defined
            if self._route.state in (RouteState.BIND, RouteState.UNBIND):
                [callback(self._route, None) for callback in brokcb]
                return

            # append watchers
            watchers = self._build._watchers[ChannelTargetState.DECLARED]
            brokcb += watchers.itervalues()

            # process
            if self._route.state != RouteState.ORIGIN_DECLARED:
                entity = self._route(broker.attrs).origin
                broker.create_entity(entity, brokcb)

            if self._route.state != RouteState.DESTINATION_DECLARED:
                entity = self._route(broker.attrs).destination
                broker.create_entity(entity, brokcb)

            # update state
            self._route.state = RouteState.UNBIND

        @engine
        def resume(self, callback=None):
            broker = self._build._broker
            brokcb = maybe_list(callback)
            brokcb.append(self._build.when_resumed)

            # append watchers
            watchers = self._build._watchers[ChannelTargetState.RESUMED]
            brokcb += watchers.itervalues()

            # don't resume again if already defined
            if self._route.state in (RouteState.BIND,):
                [callback(self._route) for callback in brokcb]
                return

            # we assume that we are on unbind state
            broker.resume_route(self._route, brokcb)

        def destroy(self, callback=None):
            raise NotImplementedError

    @engine
    def __init__(self, connection, **broker_kwargs):
        # create broker and init properties
        factory = BrokerFactory.get_instance()
        self._broker = factory.create(connection, **broker_kwargs)
        self._routes = []
        self._watchers = {
            ChannelTargetState.DECLARED:  {},
            ChannelTargetState.RESUMED:   {},
            ChannelTargetState.SUSPENDED: {},
            ChannelTargetState.DESTROYED: {},
            }

        # Channel is still undefined
        self._connection = connection

        # open a chanel if no one is available for this thread
        channel_pool = self._connection.channels
        if channel_pool.default is None:
            yield Task(self._connection.add_on_open_callback)
            yield Task(channel_pool.acquire)

        # build routes
        yield Task(self.create)
        yield Task(self.resume)

    def __iter__(self):
        return iter(self._routes)

    # virtual template methods
    def when_created(self, route, frame):
        pass

    def when_resumed(self, route, frame):
        route.state = RouteState.BIND

    def when_destroyed(self, route):
        pass

    def __call__(self, route):
        route = self.RouteBuilder(route, self)
        self._routes.append(route)
        return self

    # routes status
    def create(self, callback=None):
        """Bind all routes"""
        channel = self._connection.channels.default
        [route.create(callback) for route in self._routes]

    def resume(self, callback=None):
        channel = self._connection.channels.default
        [route.resume(callback) for route in self._routes]

    def destroy(self, callback=None):
        """Destroy route elements"""

    # watchers stuff
    def add_entity_watch(self, channel_end, target, state):
        def mentity(channel_end, route, frame):
            if hasattr(channel_end, 'exchange'):
                if channel_end.exchange == route.name:
                    channel_end.when_declared(route, frame)
            else:
                raise NotImplementedError

        def mroute(channel_end, route, frame):
            if hasattr(channel_end, 'exchange'):
                if route.origin.name in channel_end.exchange:
                    channel_end.when_resumed(route, frame)
            elif hasattr(channel_end, 'queues'):
                if route.destination.name in channel_end.queues:
                    channel_end.when_resumed(route, frame)
            else:
                raise NotImplementedError

        wid = uuid()
        matchfun = mentity if target == ChannelTarget.ENTITY else mroute
        self._watchers[state][wid] = partial(matchfun, channel_end)
        return wid

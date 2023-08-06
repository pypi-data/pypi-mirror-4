#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Routes

Represents a generic gateway to AMQP implementation
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = ['Exchange', 'Queue', 'Route']

# Project requirements
from sleipnir.core.decorators import cached

# local submodule requirements
from ..enums import RouteEndType, RouteEndPosition, RouteState, RouteType
from ..connections import ConnectionFactory
from ..parser import binding_url, URI


class RouteAbstract(object):

    ignore = []

    def __init__(self, params={}, convert={}):
        self._params = self._parse_params(params, convert)

    def __hash__(self):
        return hash(str(self))

    def __iter__(self):
        yield 'end_type', self._type
        for key, value in self._params.iteritems():
            yield key, value

    def __getattr__(self, value):
        return self._params[value]

    def _parse_params(self, params, convert):
        # convert using convert functions
        pseudo_cast = lambda v: v
        convert = convert.get(self._type, {})
        new_params = params if not convert else {}
        for key, native in convert.iteritems():
            if key in params and key not in self.ignore:
                value = (native[1] or pseudo_cast)(params[key])
                if native[2]:
                    new_params.setdefault(native[2], {})
                    new_params[native[2]][native[0]] = value
                else:
                    new_params[native[0]] = value
        return new_params

    @property
    def params(self):
        return self._params


class RouteEnd(RouteAbstract):

    ignore = ['origin', 'destination']

    def __init__(self, params={}, convert={}):
        self._name = params.get('origin', '')
        if 'origin' in self.ignore:
            self._name = params.get('destination', '')
        super(RouteEnd, self).__init__(params, convert)

    def __str__(self):
        return "%s|%s" % (self._type.enumname[0], self._name)

    @property
    def end_type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @staticmethod
    def get_type(params):
        rtype = RouteEndType.QUEUE
        if 'exchage' in params.get('type', ''):
            rtype = RouteEndType.EXCHANGE
        return rtype


class Exchange(RouteEnd):

    _type = RouteEndType.EXCHANGE

    def __init__(self, pos=RouteEndPosition.ORIGIN, args={}, convert={}):
        self.ignore = self.ignore[:]
        self.ignore.remove(pos.enumname.lower())
        super(Exchange, self).__init__(args, convert)

    def __str__(self):
        return "E|%s@%s" % (self._name, self.type)


class Queue(RouteEnd):

    _type = RouteEndType.QUEUE

    def __init__(self, pos=RouteEndPosition.DESTINATION, args={}, convert={}):
        self.ignore = self.ignore[:]
        self.ignore.remove(pos.enumname.lower())
        super(Queue, self).__init__(args, convert)


class Route(RouteAbstract):

    def __init__(self, route, state=RouteState.UNKNOWN):
        # route URI
        self._url = URI(route, binding_url)
        # Route Ends
        self._origin = self._destination = None
        # Rotute Params
        self._params = None
        # Convertion attrs
        self._convert = {}
        # Route state
        self._state = state
        # Route type
        self._type = Route.get_type(self.type)

    def __iter__(self):
        for key, value in self._url:
            if key in ("hosts", "user", "password",):
                continue
            yield key, value

    def __str__(self):
        return "R|%s@%s" % (self._url.origin, self._url.destination)

    def __repr__(self):
        return str(self._url)

    def __call__(self, convert):
        if convert != self._convert:
            self._origin = self._destination = None
            self._convert = convert
        return self

    @cached
    def params(self, convert={}):
        return self._parse_params(dict(iter(self._url)), convert)

    @cached
    def _end_params(self):
        return dict(iter(self._url))

    @property
    def name(self):
        return self._url.name

    @property
    def type(self):
        return self._url.type

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def route_type(self):
        return self._type

    @property
    def origin(self):
        if not self._origin:
            params = self._end_params()
            pos = RouteEndPosition.ORIGIN
            self._origin = Exchange(pos, params, self._convert)
        return self._origin

    @property
    def destination(self):
        if not self._destination:
            params = self._end_params()
            pos = RouteEndPosition.DESTINATION
            if RouteEnd.get_type(params) == RouteEndType.QUEUE:
                self._destination = Queue(pos, params, self._convert)
            else:
                self._destination = Exchange(pos, params, self._convert)
        return self._destination

    @property
    def url(self):
        return str(self._url)

    @staticmethod
    def get_type(str_type):
        rtype = RouteType.QUEUE
        if str_type.startswith('exchage'):
            rtype = RouteType.EXCHANGE
        return rtype

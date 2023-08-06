#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Aggregator

Base classes to implement message endpoints (EIP2003)
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = ['Aggregator']

# Project requirements
from sleipnir.core.utils import maybe_list

# local submodule requirements
from ..connections import ConnectionFactory
from .endpoints import EndPoint


class Comparator(object):

    def __init__(self, comparator):
        self._comparator = comparator
        self._operator = None
        self._value = None

    def __call__(self, body, message):
        raise NotImplementedError

    def compare(self, operator, value):
        self._operator = operator
        self._value = value
        return self

    @property
    def operator(self):
        return self._operator

    @property
    def value(self):
        self._value


class JPath(Comparator):

    import jsonpath

    def __init__(self, path):
        super(JPath, self).__init__(path)
        self._comparator = jsonpath.normalize(path)

    def __call__(self, body, message):
        match, result = None, jsonpath.jsonpath(dictionary, self._path)
        if callable(self._operator):
            match = self._operator(result, self._value)
        return result, match


class Constant(Comparator):
    def __init__(self, value=True):
        super(Constant, self).__init__(value)

    def __call__(self, body, message):
        return self._comparator, None


class Header(Comparator):
    def __call__(self, body, message):
        return (message.properties.get(self._comparator, None), None,)


# merge agregate and agregate strategy ?
class Aggregate(object):

    __slots__ = ('_request', '_message', '__weakref__')

    def __init__(self):
        self._request = None
        self._message = None

    def add_message(self, request, message):
        raise NotImplementedError

    def get_message(self):
        return self._request, self._message


class WrapperAggregate(Aggregate):

    __slots__ = ('_wrapper', '_request')

    # Wrappable Class
    wrapper = None

    def __init__(self, *args):
        super(WrapperAggregate, self).__init__()
        self._wrapper = self.wrapper(*args)
        self._message = None

    def add_message(self, request, message):
        self._message = self._message or message
        self._wrapper.add_message(message.payload)

    def is_complete(self, *args):
        return self._wrapper.is_complete(*args)

    def get_message(self):
        return self._wrapper.get_message(), self._message


# class AuctionAggregate(WrapperAggregate):

#     __slots__ = ()

#     # wrapped class
#     wrapper = Bid


# class Auction(object):

#     def __init__(self):
#         self.__bids = []

#     def add_message(self, message):
#         self.__bids.append(message)

#     def is_complete(self):
#         return len(self.__bids) > 3

#     def get_message(self):
#         winner = None
#         for bid in self.__bids:
#             winner = winner or bid
#             if int(bid['PRICE']) < int(winner['PRICE']):
#                 winner = bid
#         return winner


class LastOneAggregate(Aggregate):
    def add_message(self, request, message):
        self._request, self._message = request, message


class AggregatorFlags(enum):
    TIMEOUT,   \
    INTERVAL,  \
    SIZE,      \
    PREDICATE, \
    AGGREGATE = xrange(0, 5)


class CompletionAbstract(object):

    flag = None
    partial = None

    def __init__(self, container, value=None):
        self._container = container
        value = [self._check, self.partial, value or []]
        self._container._flags[self.flag] = value

    def _check(self, agregate):
        raise NotImplementedError


class CompletionTimeout(CompletionAbstract):

    flag = AggregatorFlags.TIMEOUT
    partial = False

    def __init__(self, container, value):
        super(CompletionTimeout, self).__init__(container, value)
        self._container.connection.add_timeout(value, self.__on_timeout)

    def __on_timeout(self):
        self._container.flags[self.flag][2] = True
        self._container.check()

    def _check(self, aggregate):
        return self._container.flags[self.flag][2] is True


class CompletionPredicate(CompletionAbstract):

    flag = AggregatorFlags.PREDICATE
    partial = True

    def _check(self, aggregate):
        args = self._container._flags[self.flag][2]
        return aggregate.is_complete(*args)


class AbstractAggregator(object):

    aggregate = LastOneAggregate

    def __init__(self, correlation, aggregate=None):

        # Aggregates storage
        self._flags = {}
        self._aggregates = {}
        self._reverse_aggregates = {}

        # Correlation stuff
        self._correlation = correlation
        self._aggregate = aggregate or self.aggregate

        # completion stuff
        self._predicate = None

        # check if whe should call is_complete for every aggregate
        # defined. This is a defualt handler. If you want to use args
        # or kwargs on is_complete method, use a CompletePredicate
        # decorator wich will override this entry
        if hasattr(self._aggregate, "is_complete"):
            CompletionPredicate(self)

    def __iter__(self):
        return self._aggregates.iteritems()

    def __len__(self):
        return len(self._aggregates)

    def _reply_on_completion(self, aggregate=None):
        # @partial: whether a match should clear all agregates and
        # start again. A false value indicates that all agregates
        # should be removed on a match
        for check, partial, value, in self._flags.itervalues():
            if check(aggregate):
                if partial:
                    aggregate_key = self._reverse_aggregates[aggregate]
                    del self._reverse_aggregates[aggregate]
                    del self._aggregates[aggregate_key]
                    self.reply(*aggregate.get_message())
                else:
                    aggrs = self._aggregates.itervalues()
                    [self.reply(*aggr.get_message()) for aggr in aggrs]
                    self.clear()
                break

    def create(self, aggregate_key, *args, **kwargs):
        aggregate = self._aggregates.get(aggregate_key)
        if not aggregate:
            aggregate = self._aggregate(*args, **kwargs)
            self._aggregates[aggregate_key] = aggregate
            self._reverse_aggregates[aggregate] = aggregate_key
        return aggregate

    def clear(self):
        self._aggregates.clear()
        self._reverse_aggregates.clear()

    def check(self, aggregate=None):
        # check completion
        aggregate = aggregate or self._aggregates.itervalues()
        [self._reply_on_completion(aggr) for aggr in maybe_list(aggregate)]

    def process(self, request, message=None):
        # get correlation key
        corkey, _ = self._correlation(request, message)
        # get aggregate, parse and check completion
        aggregate = self.create(corkey)
        aggregate.add_message(request, message)
        self._reply_on_completion(aggregate)

    def reply(self, request, message=None):
        raise NotImplementedError


class Aggregator(AbstractAggregator):
    def __init__(self, correlation, callback, aggregate=None):
        super(Aggregator, self).__init__(correlation, aggregate)
        self._callback = callback

    def reply(self, response, message):
        callbacks = maybe_list(self._callback)
        [callback(response, message) for callback in callbacks]

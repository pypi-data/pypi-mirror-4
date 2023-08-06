#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Translators

Bank instance that process loan propositions
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = ['Translator']

# Project requirements
from sleipnir.core.decorators import cached

# local submodule requirements
from itertools import izip_longest, imap, ifilter


class Translator(object):
    def __init__(self, klass=None):
        self._klasses = {}
        self._current = klass

    def __call__(self, klass):
        self._current = klass
        return self

    @cached
    def __convert(self, klass, *values):
        def fetch_class(klass):
            try:
                klass = eval(klass)
                return klass
            except:
                import inspect
                stack = inspect.stack()
                for level in xrange(len(stack) - 1, 0, -1):
                    try:
                        return stack[level][0].f_locals[klass]
                    except:
                        continue
            return None

        # init result file
        result = dict(izip_longest(imap(str, iter(klass)), (), fillvalue=None))
        # try automated adapt
        for value in ifilter(lambda x: len(x), values):
            for element, element_value in value.iteritems():
                try:
                    key = element.split('.')[1] if '.' in element else element
                    result[str(self._current(key))] = element_value
                except:
                    continue
        # use template method if any
        template = self._klasses.get(klass)
        if callable(template):
            result = template(result, klass, *values)
        return result

    def register(self, klass, template=None):
        self._klasses.setdefault(klass, template)

    def convert(self, *values):
        if self._current:
            return self.__convert(self._current, *values)
        raise NotImplementedError

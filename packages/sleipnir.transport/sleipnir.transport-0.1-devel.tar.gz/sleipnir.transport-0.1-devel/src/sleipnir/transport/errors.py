#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
exceptions

Common exceptions used by transport modules
"""

from __future__ import absolute_import

__author__  = "Carlos Martin"
__license__ = "BSD, See LICENSE file for details"

# Import here any required modules.
import sleipnir.core

__all__ = [
    'ConnectionError',
    ]


class ConnectionError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return "{0} {1}".format(self.code, self.message)


class MessageStateError(Exception):
    """The message has already been acknowledged."""
    pass

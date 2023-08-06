#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Connections

Represents a connection to an HTTP resource
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = []

# Project requirements

# local submodule requirements
from ..connections import AbstractConnection


class HTTPConnection(AbstractConnection):
    """Prepares a connection """

    def __init__(self, url, template=None):
        AbstractConnection.__init__(self, url)

    @property
    def loop(self):
        raise NotImplementedError

#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
amqparser

A handy way to parse amqp urls
"""

from __future__ import absolute_import

__author__  = "Ask Solem"
__license__ = "BSD, See LICENSE file for details"

# Import here any required modules.
try:
    from urlparse import urlparse, urlsplit
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl  # noqa

# Project requirements
from sleipnir.core.utils import kwdict, uuid

__all__ = ['amqparse', 'routeparse']


def binding_url(url):
    """
    https://cwiki.apache.org/qpid/bindingurlformat.html
    <exchange_class>://[<exchange_name>][/QueueName][?options]
    """
    parts = urlsplit(url)
    return dict({"name": uuid(),
                 "type": parts.scheme,
                 "origin": parts.netloc or "",
                 "destination": parts.path[1:] if parts.path else ""},
                **kwdict(dict(parse_qsl(parts.query))))


def connection_url(url):
    """
    amqp_url       = "amqp://" [ userinfo "@" ] addr_list [ vhost ]
    addr_list      = addr *( "," addr )
    addr           = prot_addr [ options ]
    prot_addr      = tcp_prot_addr | other_prot_addr
    vhost          = "/" *pchar [ options ]

    tcp_prot_addr  = tcp_id tcp_addr
    tcp_id         = "tcp:" / ""	; tcp is the default
    tcp_addr       = [ host [ ":" port ] ]

    other_prot_addr= other_prot_id ":" *pchar
    other_prot_id  = scheme

    options        = "?" option *( ";" option )
    option         = name "=" value
    name           = *pchar
    value          = *pchar
    """

    parts = urlsplit(url)
    addrlist = parts.netloc
    password = user = ""

    if '@' in addrlist:
        auth, _, addrlist = addrlist.partition('@')
        user, _, password = auth.partition(':')

    return dict({"type": parts.scheme,
                 "user": user,
                 "password": password,
                 "hosts": addrlist.split(','),
                 "vhost": parts.path if parts.path else ""},
                **kwdict(dict(parse_qsl(parts.query))))


class URI(object):
    def __init__(self, url, parser):
        self._urlstr = url
        self._urldct = parser(self._urlstr)

    def __str__(self):
        return self._urlstr

    def __contains__(self, item):
        return item in self._urldct

    def __iter__(self):
        return self._urldct.iteritems()

    def __getattr__(self, key):
        return self._urldct.get(key, '')

    def hosts(self):
        for addr in self._urldct["hosts"]:
            host, _, port = addr.partition(':')
            yield host, int(port or 5672)


# sugar method to register handlers
def register_scheme(scheme):
    import urlparse
    for method in filter(lambda s: s.startswith('uses_'), dir(urlparse)):
        getattr(urlparse, method).insert(0, scheme)

#connection schemas
register_scheme('amqp')
register_scheme('amqp-dev')

# binding url schemas
register_scheme('direct')
register_scheme('direct-exchange')
register_scheme('fanout')
register_scheme('fanout-exchange')
register_scheme('topic')
register_scheme('topic-exchange')

# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir Transport constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__release__          = '-devel'
__version__          = '0.1' + __release__
__date__             = '2013-7-03'
__license__          = 'GNU General Public License, version 2'

__namespace__        = "sleipnir"
__modname__          = "transport"
__appname__          = __namespace__ + '.' + __modname__

# DOAP
__title__            = 'Sleipnir Transport'
__release__          = '1'
__summary__          = 'A Wrapper around pika AMQP Library'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2011-2013 Carlos Martín'

__classifiers__      = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
    ]

__long_description__ = """
Add Here a a description to this package
"""

__requires__ = [
    'pika                     >= 0.9.6-pre0',
    'anyjson                  >= 0.3.0',
    __namespace__ + '.core    >= 0.1.93',
    ]
__tests_requires__ = [
    'pika                     >= 0.9.6-pre0',
    'anyjson                  >= 0.3.0',
    __namespace__ + '.core    >= 0.1.93',
    __namespace__ + '.testing >= 0.1rc6',
    ]

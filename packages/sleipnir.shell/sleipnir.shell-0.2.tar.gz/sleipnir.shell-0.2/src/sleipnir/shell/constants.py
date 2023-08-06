#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir Shell constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__version__          = '0.2'
__date__             = '2013-3-19'
__license__          = 'GNU General Public License, version 2'

__namespace__        = "sleipnir"
__family__           = "frontends"
__modname__          = "shell"
__appname__          = __namespace__ + '.' + __modname__
__title__            = 'Sleipnir Shell'
__release__          = '1'
__summary__          = 'A logistic system'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2011-2013 Carlos Martín'

__gettext__    = __namespace__.lower()

__classifiers__      = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    "Environment :: Handhelds/PDA's",
    "Intended Audience :: Customer Service",
    "Operating System :: POSIX :: Linux",
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    "Topic :: Office/Business :: Scheduling",
    ]

__long_description__ = """\
Add Here a a description to this package
"""

__requires__ = [
    __namespace__ + '.core       >= 0.2rc1',
    __namespace__ + '.components >= 0.2rc1',
    ]
__tests_requires__ = [
    __namespace__ + '.core       >= 0.2rc1',
    __namespace__ + '.components >= 0.2rc1',
    __namespace__ + '.testing    >= 0.1rc8',
    ]

try:
    import os
    import sys
    from sleipnir.core.decorators import cached
except ImportError:
    def cached(func):
        """Just return cached method"""
        return func


@cached
def get_basedir():
    """Get base dir for package or prefix"""
    prefix = os.path.dirname(__file__)
    prefix = os.path.normpath(os.path.join(prefix, (os.pardir + os.sep) * 4))
    return sys.prefix if prefix.startswith(sys.prefix) else prefix


@cached
def get_datadir():
    """Get data dir"""
    prefix = get_basedir()
    share = 'share' if prefix.startswith(sys.prefix) else 'data'
    return os.path.join(prefix, share)


@cached
def get_configdir():
    """Get local config dir"""
    home = os.path.join(os.environ.get('HOME', '/'), '.config')
    home = os.environ.get('XDG_CONFIG_HOME', home)
    return os.path.join(home, __namespace__, __modname__)


# pylint: disable-msg=E1101
# Common directories
__entry_point__ = __namespace__ + '.' + __family__

# Add here more constants for this project
__config_dir__ = get_configdir()
__locale_dir__ = os.path.join(get_datadir(), 'locale')

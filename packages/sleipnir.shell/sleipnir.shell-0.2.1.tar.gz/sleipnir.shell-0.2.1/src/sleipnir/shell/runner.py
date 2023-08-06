#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

""" Sleipnir Main launcher file """

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules

__all__ = ['main']


def main():
    """ main runner method entry"""

    # pylint: disable-msg=W0602
    # i18n support
    global _

    from .import constants

    # i18n stuff
    try:
        import gettext
        gettext.bindtextdomain(constants.__gettext__, constants.__locale_dir__)
        gettext.install(constants.__gettext__)
    except ImportError:
        import __builtin__
        __builtin__.__dict__['_'] = lambda s: s

    # import and run app
    from .application import Application
    Application.run()

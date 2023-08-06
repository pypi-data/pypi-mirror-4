#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Formatters

Sugar classes to present data into console
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
import sys
from textwrap import fill
from itertools import imap, chain, ifilter

__all__ = ['Help']

# Project requirements
from sleipnir.core.singleton import Singleton

# local submodule requirements


class Help(Singleton):
    """A helper to show help and usage for a command line app"""

    COMMAND_DESCRIPTION_FORMAT = {
        'width':               80,
        'initial_indent':    '  ',
        'subsequent_indent': '  ',
    }

    SHORT, LONG, VAR, HELP = xrange(4)

    def __init__(self, output=sys.stdout):
        self._output = output

    def help(self, app):
        """Shows help into output"""
        if len(app.main_opt_table):
            self.title("Main Options:")
            self.table_opt(app.main_opt_table)
        self.title("Help Options:")
        self.table_opt(app.help_opt_table)

    def help_frontends(self, app, argv):
        """Shows help for frontends"""
        self.title("Available Frontends:")
        formt = lambda x: ["%s (%s)" % (x.title, x.name), x.summary]
        table = [formt(frontend) for frontend in app.apps]
        self.table(table, format_rows=True)
        for frontend in ifilter(lambda x: x.help(argv), app.apps):
            self.title("%s Options:" % frontend.name.capitalize())
            self.table_opt(frontend.help(argv))

    def help_command(self, txt):
        """Shows help for commands"""
        self.title("%s: A %s" % (txt[0], txt[1]))  # short description
        self.title(fill(txt[2], **self.COMMAND_DESCRIPTION_FORMAT))
        self.title("%s Options:" % txt[0])
        self.table_opt(txt[3])

    def title(self, title):
        """Prints a title"""
        self._output.write(title + '\n')

    def table(self, table, format_rows=False):
        """Formats a list as an arguments table"""
        pad = 5 if format_rows else 0
        tbl = imap(lambda x: len(x[0]) + pad, table)
        mlen = max(*(chain(tbl, [0, 0])))
        for opt, description in table:
            opt = "  " + opt + ":  " if format_rows else opt
            txt = opt.ljust(mlen) + description
            txt = fill(txt, width=80, subsequent_indent=' ' * mlen)
            self._output.write(txt + '\n')
        self._output.write('\n')

    def table_opt(self, table):
        """Process a GNU GetOpt Like table"""
        opt_list = []
        for row in table:
            opt = "".join((row[Help.SHORT], ", ", row[1])) \
                if row[Help.SHORT] else row[Help.LONG]
            opt = "".join((opt, "=<", row[Help.VAR], ">")) \
                if row[Help.VAR] else opt
            opt_list.append(["".join(("  ", opt, "  ")), row[Help.HELP]])
        self.table(opt_list)

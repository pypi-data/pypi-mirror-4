#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Arguments

A Custom argument parser for sleipnir
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
from itertools import ifilter
from optparse import OptionParser

__all__ = ['Options']

# Project requirements
from sleipnir.core.singleton import Singleton

# local submodule requirements


#pylint: disable-msg=R0921
class Options(Singleton):
    """
    A custom argument parser container that allow for hierachy child
    arguments
    """

    abstract = True

    def __init__(self, argv):
        self._parser = Parser(root=self)
        self._args   = argv
        self._values = {}
        self._remain_args = []

    def __iter__(self):
        return iter(self._parser)

    def __getattr__(self, value):
        # try an option
        if value in self._values:
            return self._values[value]

        # if not, try a parser method
        if hasattr(self._parser, value):
            return getattr(self._parser, value)

        # not found? raise esception
        raise AttributeError(value)

    @property
    def options(self):
        """Get current available values"""
        return self._values

    @property
    def args(self):
        """Get arguments to be parsed"""
        return self._args

    @property
    def remain_args(self):
        """Leftover arguments after a call to parse"""
        return self._remain_args

    def parse(self, args, parser=None, recursive=0):
        """Parse command line"""
        parser  = self.children.get(parser, self._parser)
        _, argv = parser.parse_arguments(args)
        remain  = parser.children.values()
        while (recursive != 0 and len(remain) > 0):
            children, recursive = [], -1
            for child in remain:
                _, argv = child.parse_arguments(argv)
                children.extend(child.children.itervalues())
            remain = children
        self._remain_args = argv

    def find(self, name):
        """Lookup for name into args"""
        raise NotImplementedError

    def find_by_option(self, option):
        """Lookup for option in args"""
        raise NotImplementedError


class ParserOptions(enum):
    """Parser options"""
    short, long, default, help, action, dest, recursive = xrange(7)
    
    
#pylint: disable-msg=R0904
class Parser(OptionParser):
    """Custom Parser"""

    def __init__(self, root):
        OptionParser.__init__(self, add_help_option=False)
        self._root = root
        self._children = {}
        self._recursive_options = []

    @property
    def children(self):
        """Get associated parsers"""
        return self._children

    def add_options(self, opt_table):
        """Parse and aggregate contents of option table"""

        # sugar to add opt table
        valid = ("store_const", "store_true", "store", "store_false",)
        kasis = ("help", "dest", "default", "action",)

        for opt in opt_table:
            # action contains also type
            kwargs = dict((k, opt[int(ParserOptions(k))]) for k in kasis)
            action = opt[int(ParserOptions('action'))]
            if action and action not in valid:
                kwargs['action'], kwargs['type'] = action.split('_')
            # now add option
            self.add_option(*opt[:2], **kwargs)

        # add child options if any
        rec_index = int(ParserOptions('recursive'))
        re_filter = lambda x: len(x) > rec_index and x[rec_index]
        for opt in ifilter(re_filter, opt_table):
            self._recursive_options.append(opt)
            for child in self._children.itervalues():
                child.add_options([opt])

    def add_child_options(self, name, opt_table):
        """Add opt table to child named. If not exists, create one"""
        add_recursive_options = name in self._children
        parser = self._children.setdefault(name, Parser(root=self._root))
        if add_recursive_options:
            parser.add_options(self._recursive_options)
        parser.add_options(opt_table)
        return parser

    def parse_arguments(self, argv):
        """validate arguments and estract options from argv"""

        # validate entry
        index, fargv = 1, []
        while (index < len(argv)):
            next_opt = argv[index]
            if "=" in next_opt:
                next_opt, _ = next_opt.split("=", 1)
            option = self.get_option(next_opt)
            if not option:
                if not next_opt or next_opt[0] == '-':
                    index += 1
                    continue
                fargv = [argv[0]] + argv[index:]
                break
            if option.action != 'callback':
                nparam = (option.nargs or 1)
                index += 1 + (0 if len(next_opt) != len(argv[index]) else nparam)
            else:
                raise NotImplementedError("Usupported action: 'callback'")
        main = argv[:index]
        options, _ = self.parse_args(main)
        self._root.options.update(vars(options))
        return main, fargv

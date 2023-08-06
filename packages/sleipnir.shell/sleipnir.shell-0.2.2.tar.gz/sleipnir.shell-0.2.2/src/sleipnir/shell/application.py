# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Application

Main Application Component Manager
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
import sys
import os.path
from itertools import ifilter, chain
from operator import attrgetter

__all__ = ['Application']

# Project requirements
from sleipnir.components.manager import ComponentManager
from sleipnir.components.entrypoint import ExtensionPoint
from sleipnir.components.loaders import LoaderManager
from sleipnir.components.components import Component

# local submodule requirements
from .interfaces import application
from .formatters import Help
from .arguments import Options
from .import constants


class Parser(Options):
    """Sleipnir custom parser"""

    @property
    def command(self):
        """sugar property to get command or frontend property"""
        args = self._remain_args
        return args[1] if len(args) >= 2 and args[1][0] != '-' else None


#pylint: disable-msg=R0903
class Application(ComponentManager, Component):
    """
    ComponentManager to instantiate 'IApplication' implementations
    based on runned system or argv options
    """
    apps = ExtensionPoint(application.IApplication)
    instance = None

    main_opt_table = [
        ["-p", "--profiles", "",
         "Limit behaviour to PROFILES", "store", "profiles"],
    ]

    help_opt_table = [
        ["-v", "--version", None,
         "Show version", "store_true", "version", True],
        ["-h", "--help", None,
         "Show help", "store_true", "help", True],
        ["", "--help-frontends", None,
         "List available frontends", "store_true", "help_frontends"],
        ["", "--help-commands", None,
         "List available commands", "store_true", "help_commands"],
    ]

    def __init__(self, output=sys.stdout, parser=None):
        super(Application, self).__init__()
        self._parser = parser
        self._output = output
        self._loader = LoaderManager(self)
        self._loader.load(entry_points=constants.__entry_point__)

    @property
    def parser(self):
        """Get instance parser"""
        return self._parser

    def usage(self, argv):
        """Show command usage when invoked from command line"""

        cmd = os.path.basename(argv[0])
        # Main Usage
        self._output.write(
            "Usage: %s [global_opts] [backend [backend_opts]] "
            "[cmd [cmd_opts]]\nor: %s --help-frontends\n" % (cmd, cmd))
        # Application Usages
        [self._output.write(app.usage(argv) or "") for app in self.apps]
        self._output.write("\n")
        # Now show help
        self.help(argv)

    def help(self, argv):
        """Show help"""

        helper = Help.get_instance(self._output)
        if any((self._parser.help, self._parser.help_frontends)):
            helper.help(self)

        if self._parser.help_frontends:
            helper.help_frontends(self, argv)

        if self._parser.help_commands:
            for app in self.apps:
                for cat, table in app.help_commands() or []:
                    name = app.name.capitalize()
                    title = "'%s' commands on '%s' frontend:"
                    helper.title(title % (cat.capitalize(), name))
                    helper.table(table, format_rows=True)

    @classmethod
    def run(cls, argv=sys.argv):
        "Invoke application"

        # init command line parser
        parser = Parser.get_instance(argv)
        parser.add_options(chain(cls.help_opt_table, cls.main_opt_table))
        parser.parse(parser.args, recursive=0)

        # peek current instance or create a new one
        assert not cls.instance
        cls.instance = cls(parser=parser)

        # process help command
        if any((parser.help, parser.help_frontends, parser.help_commands)):
            cls.instance.usage(argv)
            return 0
        # process version command
        if parser.version:
            cls.instance.version(argv)
            return 0

        # validate entry
        apps = cls.instance.apps
        # Now try to invoke a frontend. If fails. try with a command
        if parser.command is not None:
            # try a frontend
            ffilter = lambda x: x.name == parser.command
            for app in ifilter(ffilter, apps):
                parser.remain_args.pop(1)
                return app.run(parser.remain_args)
            # finally try a command
            for app in apps:
                if len(app.commands(parser.command)) == 1:
                    return app.run(parser.remain_args)
            else:
                sys.stderr.write("Unknown parameter '%s'\n" % parser.command)
                return -1

        for app in sorted(apps, key=attrgetter('runnable')):
            return app.run(parser.remain_args)
        sys.stderr.write("No valid frontends available\n")
        return -1

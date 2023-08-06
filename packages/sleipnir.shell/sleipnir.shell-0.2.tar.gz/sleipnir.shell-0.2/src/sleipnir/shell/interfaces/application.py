#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Shell application Interfaces"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.

__all__ = ['IApplication', ]

# Project Dependences
from sleipnir.components.entrypoint import Interface


# pylint: disable-msg=W0232, R0921
class IApplication(Interface):
    """
    Base interface required to be implemented by TSP related applications
    """

    INVALID, SUGGESTED, VALID, RECOMMENDED = xrange(4)

    @property
    def name(self):
        """Applications's shotname"""
        raise NotImplementedError

    @property
    def title(self):
        """Application's name"""
        raise NotImplementedError

    @property
    def summary(self):
        """Application's summary"""
        raise NotImplementedError

    @property
    def version(self):
        """Application's version"""
        raise NotImplementedError

    @property
    def copyright(self):
        """Author's details"""
        raise NotImplementedError

    @property
    def doap(self):
        """Returns description of project"""
        raise NotImplementedError

    @property
    def runnable(self):
        """Returns wherther application can run under user environment"""

    def usage(self, argv):
        """Return a raw string for custom usage for this  application"""
        raise NotImplementedError

    def help(self, argv):
        """Returns a raw string with help usage"""
        raise NotImplementedError

    def help_commands(self, command=None):
        """
        Returns help info for command parameter or a list of valid
        commands if no command is present
        """
        raise NotImplementedError

    def commands(self, name=None):
        """
        Returns a list of available commands for this backend
        """
        raise NotImplementedError

    def run(self, argv, **kwargs):
        "Invoke main loop in application"
        raise NotImplementedError

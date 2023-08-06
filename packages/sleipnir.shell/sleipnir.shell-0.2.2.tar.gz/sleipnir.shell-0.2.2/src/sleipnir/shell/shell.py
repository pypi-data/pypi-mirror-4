# -*- mode:python; coding: utf-8 -*-

"""
Shell

Main Shell instance
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
import os

__all__ = ['Shell']

# Project requirements
from sleipnir.core.singleton import Singleton
from sleipnir.core.memoizer import Memoizer

# local submodule requirements
from .constants import get_configdir


class ShellError(Exception):
    """Shell Main exception"""


#pylint: disable-msg=E1101,R0921
class Shell(Singleton):
    """ Main Shell"""

    def __init__(self, name, args=None):
        self._name = name
        self._args = args
        # Create key/value store
        store = os.path.join(get_configdir(), "{0}.shellcache".format(name))
        # Use failover with None as default/missing value
        self._values = Memoizer(store=store, failover=None)
        # known objects values. Contains non trivial objects that will
        # be destroyed with Shell on exit
        self._instances = {}

    @property
    def name(self):
        """Shell application unique name"""
        return self._name

    @property
    def session(self):
        """Get hash elements"""
        return self._values

    @property
    def instances(self):
        """Get registered objects"""
        return self._instances

    def insert(self, name, value, expires=Memoizer.LIFETIME):
        """
        Sets a value in the shell with the given name. Any previous
        value will be overridden. "value_changed" signal will be
        emitted. Objects connecting to this signal can then update
        their data according to the new value.
        """
        assert name not in self._instances
        self._values.set(name, value, expires)

    def remove(self, name):
        """
        Removes name from values. If not exists, raise a
        ShellError. Previously to remove data, a value_removed is
        fired
        """
        assert name in self._values
        self._values.delete(name)

    def register(self, name, value):
        """
        Register a value as a known object. Changes aren't propagated
        for this kind of values
        """
        return self._instances.setdefault(name, value)

    def quit(self):
        """Quits shell"""
        # purge obsolete values
        self._values.purge()
        # save to disk
        self._values.sync()

    def run(self, options, *extra_args):
        """Starts Application"""
        raise NotImplementedError

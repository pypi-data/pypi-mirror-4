# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Shell

Main Shell instance
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules

__all__ = ['Shell']

# Project requirements
from sleipnir.core.singleton import Singleton

# local submodule requirements
from .signals import Signal


class ShellError(Exception):
    """Shell Main exception"""


#pylint: disable-msg=E1101,R0921
class Shell(Singleton):
    """ Main Shell"""

    # Quit notifier
    leave = Signal()

    # Signals
    value_changed = Signal()
    value_removed = Signal()

    def __init__(self, name, args=None):
        self._name = name
        self._args = args
        # value subsystem
        self._values = {}
        self._known_objects = {}

    def __getattr__(self, name):
        try:
            return self._values[name]
        except KeyError:
            # Not Found? Raise an error
            raise ShellError("Session key '%s' not registered yet", name)

    def __iter__(self):
        return self._values.iterkeys()

    @property
    def name(self):
        """Shell application unique name"""
        return self._name

    @property
    def objects(self):
        """Get registered objects"""
        return self._known_objects

    def insert(self, name, value):
        """Helper to update method"""
        self.update(name, value, False)

    def update(self, name, value, notify=True):
        """
        Sets a value in the shell with the given name. Any previous
        value will be overridden. "value_changed" signal will be
        emitted. Objects connecting to this signal can then update
        their data according to the new value.
        """
        if name in self._known_objects:
            self._known_objects[name] = value
        else:
            self._values[name] = value
            #pylint: disable-msg=W0106
            notify and self.value_changed.emit(name)

    def remove(self, name):
        """
        Removes name from values. If not exists, raise a
        ShellError. Previously to remove data, a value_removed is
        fired
        """
        assert name in self._values
        if name in self._values:
            self.value_removed.emit(name)
            del self._values[name]

    def register(self, name, value):
        """
        Register a value as a known object. Changes aren't propagated
        for this kind of values
        """
        return self._known_objects.setdefault(name, value)

    def quit(self):
        """Quits shell"""
        self.leave.emit()

    def run(self, options, *extra_args):
        """Starts Application"""
        raise NotImplementedError

#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Signals

Signals wrappers for different signals technologies
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
from sys import _getframe, modules

__all__ = ['SignalFactory', 'Signal']

# Project requirements
from sleipnir.core.factory import AbstractFactory
from sleipnir.core.event import Event

# local submodule requirements


#pylint: disable-msg=W0232, R0903
class SignalAbstractFactory(AbstractFactory):
    """Main Private signal factory"""


class MetaSignal(type):
    """Signal Metaclass"""
    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if hasattr(mcs, 'create'):
            platform = mcs.platform()
            sfactory = SignalAbstractFactory.get_instance()
            if platform is not None:
                sfactory.register(platform, mcs)
            sfactory.register(name[:-6], mcs)


class SignalFactory(object):
    """Base class from which derive Signal factories"""

    __metaclass__ = MetaSignal

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        """Get signal name"""
        return self._name

    @classmethod
    def platform(cls):
        """Get signal technology"""
        return None


class Signal(object):
    """
    Signal Ghost class

    This class take into account frame from declared class to
    establish signal name, and determine selected platform to be used
    based on current loaded modules
    """
    #pylint: disable-msg=C0103
    class __metaclass__(type):
        """Signal Magic"""
        def __call__(mcs, *args, **kwargs):
            factory = SignalAbstractFactory.get_instance()
            # Process kwargs, if name not in kwargs, unse introspection
            # to fetch Signal name from asigned variable
            name = kwargs.get('name', None)
            if name is None:
                frame = _getframe(1)
                local = frame.f_locals.keys()
                conms = frame.f_code.co_names
                names = [name for name in conms if not name.startswith('__')]
                for index, posible in enumerate(names):
                    if posible not in local:
                        index = min(index + 1, len(names) - 1)
                        kwargs.setdefault('name', names[index])
                        break
                del frame
            if 'name' not in kwargs:
                raise TypeError("Anonymous signals aren't allowed")

            platform = kwargs.get('platform', None)
            if platform is None:
                for platform in factory.backends.iterkeys():
                    if platform in modules:
                        break
            platform = platform or 'Python'
            # Not instantiate a Signal instance
            factory = factory.backends[platform]
            return factory.create(*args, **kwargs)


class PythonSignal(SignalFactory):
    """Dispatcher based signal factory"""

    #pylint: disable-msg=E0211
    @classmethod
    def create(cls, *args, **kwargs):
        """Creates a Signal"""
        return Event(*args, **kwargs)

#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Platform detector

Checks and returns platform on which current softwarer is running
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
from operator import attrgetter
from os import path, makedirs, unlink, getpid
from itertools import ifilter

__all__ = ['Platform']

# Project requirements
from sleipnir.core.factory import AbstractFactory
from sleipnir.core.singleton import Singleton
from sleipnir.core.decorators import cached
from sleipnir.core.log import log

# local submodule requirements

LAST_PRIORITY =  1000000
REAL_PRIORITY =  0
WRAP_PRIORITY = -1


class Platform(Singleton):
    """Checks and Returns data about current platform"""

    def __init__(self):
        self._factory = PlatformFactory.get_instance()
        self._target  = None

    def __iter__(self):
        return iter(self._factory)

    @property
    def name(self):
        """Get platform name for target or fallback to real"""
        return self.target.name if self.target else self.real.name

    @property
    @cached
    def real(self):
        """Sort platforms based on idoneity and PRIORITY"""
        platform = self._factory.recommended
        return platform()

    @property
    def target(self):
        """Returns target platform"""
        return self._target

    @target.setter
    def target(self, value):
        """Set target platform"""
        # Store
        self._target = value

        # PlatformWrapper is a catch all class. If we don't support
        # platform yet, PlatformWrapper provides a set of probably
        # broken values
        if isinstance(value, basestring):
            try:
                # Now lookup for a valid platform
                self._target = next(ifilter(lambda x: value in x.NAMES, self))
            except StopIteration:
                # Fallback to a wrapper
                self._target = PlatformWrapper(value)

    def lock(self, name, action):
        """Set or clear lock"""
        return self.real.lock(name, action)

        
class PlatformFactory(AbstractFactory):
    """Checks and Returns data about current platform"""

    def __iter__(self):
        return iter(self.available)

    @property
    @cached
    def recommended(self):
        """Peek the first valid platform sorted by PRIORITY"""
        return next(ifilter(lambda x: x.match(), self.available))

    @property
    @cached
    def available(self):
        """Return an iterable of available platforms"""
        iterable  = self.backends.itervalues()
        return sorted(iterable, key=attrgetter('PRIORITY'))


#pylint: disable-msg=R0903
class PlatformWrapper(object):
    """A method delegator pattern for platforms"""

    PRIORITY  = WRAP_PRIORITY
    
    def __init__(self, value):
        if isinstance(value, basestring):
            values = (value.lower(), value.upper(), value.capitalize(),)
            value = PlatformMixin(values)
        self._value = value

    def __getattr__(self, name):
        return getattr(self._value, name)

        
class MetaPlatform(type):
    """Platform register metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        factory = PlatformFactory.get_instance()
        mcs.NAMES and factory.register(name, mcs)


class PlatformMixin(object):
    """Base class to represent platforms"""

    __metaclass__ = MetaPlatform
    
    NAMES     = []
    PRIORITY  = LAST_PRIORITY
    WHERELOCK = "/tmp/var/run/lock/%s"
    
    def __init__(self, names=None):
        self._names = names or self.NAMES

    def __contains__(self, value):
        return value in self._names

    @property
    def names(self):
        """Gets a collection of valid names for platform"""
        return self._names

    @property
    def name(self):
        """Get platform id"""
        return self._names[0].lower()

    @property
    def graphics_system(self):
        """Get valid graphics system for platform"""
        return [None, None]

    @property
    def flavor(self):
        """Get os variants"""
        return None

    @classmethod
    def match(cls):
        """Verify that platform is applicable or not"""
        return True

    @classmethod
    def lock(cls, name, action):
        """Try to adquire or clear lock"""

        def _lock(lock_file):
            """Sugar method to try to adquire a lock to a file"""
            import fcntl
            # Fails if dirs already exits
            try:
                makedirs(cls.WHERELOCK % name)
            except OSError, err:
                pass
            # now lock
            if not path.exists(lock_file):
                with file(lock_file, "w") as lfd:
                    try:
                        fcntl.lockf(lfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        lfd.write("%d\n" % getpid())
                        return True
                    except IOError:
                        pass
            return False
            
        lfile = path.join(cls.WHERELOCK % name, "%s.%s" % (name, "lock"))
        try:
            if action and action[0] == 'l':
                if not _lock(lfile):
                    owner = getpid()
                    with file(lfile, "r") as lfd:
                        owner = int(lfd.readline() or "-1")
                        if not path.exists("/proc/%d" % owner):
                            unlink(lfile)
                            return -1
                    if owner != getpid():
                        return owner
                return 0
            else:
                unlink(lfile)
                return 0
        except OSError, err:
            log.core.error(err)

            
class Desktop(PlatformMixin):
    """Base class for command objects"""

    NAMES = ["DESKTOP", "desktop", "Desktop"]

        
class QtBase(PlatformMixin):
    """Base class for apps that requires PySide"""

    @property
    def graphics_system(self):
        return ["raster", None]


class Simulator(QtBase):
    """A base class for Simulator instances"""

    PRIORITY = LAST_PRIORITY - 1
    NAMES    = ["SIMULATOR", "simulator", "Simulator"]

    def lock(self, name, action):
        # Always success
        return 0
        
    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        # First, check for PySide. If not present, we are not in
        # Simulator
        try:
            __import__ ('PySide')
        except ImportError:
            return False
        # Check for QPrinter. This exists on Maemo :O and desktop but
        # not in simulator
        try:
            __import__('PySide.QtGui.QPrinter')
            return False
        except ImportError:
            return True


class Fremantle(QtBase):
    """A Base class for Harmattan instances"""

    PRIORITY = REAL_PRIORITY
    NAMES    = ["FREMANTLE", "Fremantle", "fremantle"]
    
    @property
    @cached
    def flavor(self):
        if path.exists('/var/lib/dpkg/info/mp-fremantle-generic-pr.list'):
            return "ssu"
        if path.exists('/var/lib/dpkg/info/mp-fremantle-community.list'):
            return "cssu" 
        #fallback. Probably used on a fake environment
        return super(QtBase, self).flavor

    @property
    def graphics_system(self):
        return ["raster", None] if self.flavor == "ssu" else ["opengl", None]

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        return path.exists('/var/lib/dpkg/info/mp-fremantle-generic-pr.list')


class FremantleSSU(PlatformMixin):

    PRIORITY = REAL_PRIORITY
    NAMES    = ["FREMANTLE-SSU", "Fremantle-ssu", "fremantle-ssu"]

    @property
    def flavor(self):
        return "ssu"

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        return False

class FremantleCSSU(PlatformMixin):

    PRIORITY = REAL_PRIORITY
    NAMES    = ["FREMANTLE-CSSU", "Fremantle-cssu", "fremantle-cssu"]

    @property
    def flavor(self):
        return "cssu"

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        return False


class Harmattan(QtBase):
    """A Base class for Harmattan instances"""

    PRIORITY  = REAL_PRIORITY
    NAMES     = ["HARMATTAN", "Harmattan", "harmattan"]
    WHERELOCK = "/var/run/single-instance-locks/opt/%s"

    @property
    def graphics_system(self):
        return ["runtime", None]

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        try:
            with open('/etc/issue') as issue:
                if ('Harmattan' in issue.read()):
                    return True
                return False
        except Exception:
            return False


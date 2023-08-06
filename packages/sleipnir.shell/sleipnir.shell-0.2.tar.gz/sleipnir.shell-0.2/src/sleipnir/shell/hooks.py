#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Loads and executes user hooks.

Hooks are python scripts in ~/.config/sleipnir/hooks. Each script must
define a class named "SleipnirHooks", otherwise it will be ignored.

The hooks class defines several callbacks that will be called by the
Sleipnir application at certain points. See the methods defined below
for a list on what these callbacks are and the parameters they take.

For an example extension see doc/dev/examples/hooks.py
"""
from __future__ import absolute_import

__author__    = "Carlos Martin <cmartin@liberalia.net>"
__license__   = "GPL3"
__copyright__ = "2005-2009 Thomas Perl and the gPodder Team"

# Import here any required modules
import glob
import imp
import os
import functools

__all__ = ['HookManager', 'call_hooks']

# Project requirements
from sleipnir.core.log import log

# local submodule requirements
from .constants import __config_dir__


def call_hooks(func):
    """
    Decorator to create handler functions in HookManager. Calls the
    specified function in all user extensions that define it.
    """
    method_name = func.__name__

    @functools.wraps(func)
    def handler(self, *args, **kwargs):
        """Decorator"""
        for filename, module in self.modules:
            try:
                callback = getattr(module, method_name, None)
                callback(*args, **kwargs)
            except TypeError, ex:
                log.hooks.debug(
                    "In %s:, function %s not callable", filename, method_name)
            except Exception, ex:
                log.hooks.debug(
                    'In %s, function %s: %s', filename, method_name, ex)
        # Invoke func
        func(self, *args, **kwargs)
    return handler


class HookManager(object):
    """The class name that has to appear in a hook module"""

    HOOK_CLASS = 'SleipnirHooks'

    def __init__(self):
        """Create a new hook manager"""

        def _load_module(filepath):
            """
            Load a Python module by filename

            Returns an instance of the HOOK_CLASS class defined in the
            module, or None if the module does not contain such a class.
            """
            basename, extension = os.path.splitext(os.path.basename(filepath))
            module = imp.load_module(
                basename,
                file(filepath, 'r'),
                os.path.dirname(filepath),
                (extension, 'r', imp.PY_SOURCE))
            hook_class = getattr(module, HookManager.HOOK_CLASS, None)
            return None if hook_class is None else hook_class()

        self.modules = []
        for fname in glob.glob(os.path.join(__config_dir__, 'hooks', '*.py')):
            try:
                module = _load_module(fname)
                if module is not None:
                    self.modules.append((fname, module))
                    log.hooks.info('Module loaded: %s', fname)
            #pylint: disable-msg=W0703
            except Exception, ex:
                log.hooks.debug('In loading %s: %s', fname, ex)

    def has_modules(self):
        """
        Check whether this manager manages any modules

        Returns True if there is at least one module that is managed
        by this manager, or False if no modules are loaded (in this
        case, the hook manager can be deactivated).
        """
        return bool(self.modules)

    # Define all known handler functions here, decorate them with the
    # "call_hooks" decorator to forward all calls to hook scripts that have
    # the same function defined in them. If the handler functions here contain
    # any code, it will be called after all the hooks have been called.

    @call_hooks
    def on_class_method(self, class_instance):
        """Example hook method"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Event emitter system for rumps."""

import traceback
from ..utils.internal import call_as_function_or_method


class EventEmitter(object):
    """
    Event emitter for handling callbacks in rumps applications.

    This class manages event callbacks and emits events to all registered handlers.
    """

    def __init__(self, name):
        """
        Initialize an EventEmitter.

        Args:
            name: The name of the event emitter for debugging purposes.
        """
        self.name = name
        self.callbacks = set()
        self._executor = call_as_function_or_method

    def register(self, func):
        """
        Register a callback function for this event.

        Args:
            func: The callback function to register.

        Returns:
            The registered function (for decorator use).
        """
        self.callbacks.add(func)
        return func

    def unregister(self, func):
        """
        Unregister a callback function from this event.

        Args:
            func: The callback function to unregister.

        Returns:
            True if the function was unregistered, False if it wasn't registered.
        """
        try:
            self.callbacks.remove(func)
            return True
        except KeyError:
            return False

    def emit(self, *args, **kwargs):
        """
        Emit the event to all registered callbacks.

        Args:
            *args: Positional arguments to pass to callbacks.
            **kwargs: Keyword arguments to pass to callbacks.
        """
        for callback in self.callbacks:
            try:
                self._executor(callback, *args, **kwargs)
            except Exception:
                traceback.print_exc()

    __call__ = register  # Allow using the emitter as a decorator
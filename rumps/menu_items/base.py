#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Base abstract class for all menu items in rumps."""

from abc import ABC, abstractmethod
import sys

if sys.version_info[0] <= 2:
    string_types = basestring
else:
    string_types = str

try:
    from typing import Optional, Callable, Any
except ImportError:
    Optional = Callable = Any = None


class BaseMenuItem(ABC):
    """
    Abstract base class for all menu items in rumps.

    Provides common interface and functionality for menu items.
    """

    def __init__(self):
        """Initialize base menu item properties."""
        self._menuitem = None
        self._callback = None
        self._view = None

    @property
    @abstractmethod
    def callback(self):
        """
        Return the current callback function.

        Returns:
            The callback function or None
        """
        pass

    @abstractmethod
    def set_callback(self, callback, *args, **kwargs):
        """
        Set the callback function for this menu item.

        Args:
            callback: Function to call when menu item is activated
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        pass

    @property
    def menuitem(self):
        """
        Return the underlying NSMenuItem object.

        Returns:
            NSMenuItem instance or None
        """
        return self._menuitem

    @property
    def view(self):
        """
        Return the NSView if this is a view-based menu item.

        Returns:
            NSView instance or None
        """
        return self._view

    @property
    def enabled(self):
        """
        Check if the menu item is enabled.

        Returns:
            bool: True if enabled, False otherwise
        """
        if self._menuitem:
            return self._menuitem.isEnabled()
        return False

    @enabled.setter
    def enabled(self, value):
        """
        Enable or disable the menu item.

        Args:
            value (bool): True to enable, False to disable
        """
        if self._menuitem:
            self._menuitem.setEnabled_(bool(value))

    @property
    def hidden(self):
        """
        Check if the menu item is hidden.

        Returns:
            bool: True if hidden, False otherwise
        """
        if self._menuitem:
            return self._menuitem.isHidden()
        return False

    @hidden.setter
    def hidden(self, value):
        """
        Show or hide the menu item.

        Args:
            value (bool): True to hide, False to show
        """
        if self._menuitem:
            self._menuitem.setHidden_(bool(value))

    def hide(self):
        """Hide the menu item."""
        self.hidden = True

    def show(self):
        """Show the menu item."""
        self.hidden = False

    def _register_with_app(self, nsapp_dict):
        """
        Register this menu item with the NSApp callback dictionary.

        This is a common registration pattern used across menu items.

        Args:
            nsapp_dict: The NSApp callback dictionary
        """
        pass

    def __repr__(self):
        """
        Return string representation of the menu item.

        Returns:
            str: String representation
        """
        callback_name = 'None'
        if self.callback:
            callback_name = getattr(self.callback, '__name__', repr(self.callback))
        return '<{0}: callback={1}>'.format(type(self).__name__, callback_name)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""ListMenuItem and ListView classes for rumps."""

from AppKit import NSView, NSMenuItem, NSApp, NSMakeRect

from .base import BaseMenuItem


class ListMenuItem(BaseMenuItem):
    """
    Represents a list menu item within the application's menu.

    NOTE: This is a placeholder implementation. The full implementation
    requires extracting the complex NSTableView-based logic from rumps.py.
    """

    def __init__(self, items=None, selected=None, callback=None, dimensions=(200, 150)):
        super(ListMenuItem, self).__init__()
        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, *dimensions))
        self._menuitem = NSMenuItem.alloc().init()
        self._menuitem.setView_(self._view)
        self._items = items or []
        self._selected = selected
        self._callback = callback

    @property
    def callback(self):
        return self._callback

    def set_callback(self, callback, *args, **kwargs):
        self._callback = callback


class ListView(BaseMenuItem):
    """
    Represents a list view menu item within the application's menu.

    NOTE: This is a placeholder implementation. The full implementation
    requires extracting the complex NSTableView-based logic from rumps.py.
    """

    def __init__(self, items=None, callback=None, dimensions=(200, 150)):
        super(ListView, self).__init__()
        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, *dimensions))
        self._menuitem = NSMenuItem.alloc().init()
        self._menuitem.setView_(self._view)
        self._items = items or []
        self._callback = callback

    @property
    def callback(self):
        return self._callback

    def set_callback(self, callback, *args, **kwargs):
        self._callback = callback
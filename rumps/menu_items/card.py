#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""CardMenuItem class for rumps."""

from AppKit import NSView, NSMenuItem, NSApp, NSMakeRect

from .base import BaseMenuItem


class CardMenuItem(BaseMenuItem):
    """
    Represents a card-style menu item within the application's menu.

    NOTE: This is a placeholder implementation. The full implementation
    requires extracting the complex card layout logic from rumps.py.
    """

    def __init__(self, title="", subtitle="", icon=None, callback=None, dimensions=(250, 60)):
        super(CardMenuItem, self).__init__()
        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, *dimensions))
        self._menuitem = NSMenuItem.alloc().init()
        self._menuitem.setView_(self._view)
        self._title = title
        self._subtitle = subtitle
        self._icon = icon
        self._callback = callback

    @property
    def callback(self):
        return self._callback

    def set_callback(self, callback, *args, **kwargs):
        self._callback = callback
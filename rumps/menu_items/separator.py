#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""SeparatorMenuItem class for rumps."""

from AppKit import NSMenuItem

from .base import BaseMenuItem


class SeparatorMenuItem(BaseMenuItem):
    """Visual separator between MenuItem objects in the application menu."""

    def __init__(self):
        super(SeparatorMenuItem, self).__init__()
        self._menuitem = NSMenuItem.separatorItem()

    @property
    def callback(self):
        """Separator items don't have callbacks."""
        return None

    def set_callback(self, callback, *args, **kwargs):
        """Separator items cannot have callbacks."""
        pass


# Convenience object - matches the original rumps.separator behavior
# This is just a sentinel object, not an actual SeparatorMenuItem instance
separator = object()
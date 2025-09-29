#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""
ListDict: OrderedDict subclass with insertion methods for modifying
the order of the linked list in O(1) time.

https://gist.github.com/jaredks/6276032
"""

from ..packages.ordereddict import OrderedDict as _OrderedDict


class ListDict(_OrderedDict):
    """OrderedDict with O(1) insertion operations."""

    def __insertion(self, link_prev, key_value):
        key, value = key_value
        if link_prev[2] != key:
            if key in self:
                del self[key]
            link_next = link_prev[1]
            self._OrderedDict__map[key] = link_prev[1] = link_next[0] = [link_prev, link_next, key]
        dict.__setitem__(self, key, value)

    def insert_after(self, existing_key, key_value):
        """Insert key_value after existing_key."""
        self.__insertion(self._OrderedDict__map[existing_key], key_value)

    def insert_before(self, existing_key, key_value):
        """Insert key_value before existing_key."""
        self.__insertion(self._OrderedDict__map[existing_key][0], key_value)
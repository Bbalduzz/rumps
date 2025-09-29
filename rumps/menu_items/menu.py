#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Menu class for rumps."""

import AppKit
from AppKit import NSMenu, NSMakeRect, NSSize

from ..utils import ListDict
from ..utils.helpers import _log
from ..utils.compat import string_types, iteritems, collections_abc


class Menu(ListDict):
    """
    Wrapper for Objective-C's NSMenu class.

    Implements core functionality of menus in rumps. MenuItem subclasses Menu.
    Only ever used as the main menu since every other menu would exist as a submenu of a MenuItem.
    """

    _choose_key = object()

    def __init__(self):
        self._counts = {}
        if not hasattr(self, '_menu'):
            self._menu = NSMenu.alloc().init()
        super(Menu, self).__init__()

    def __setitem__(self, key, value):
        if key not in self:
            key, value = self._process_new_menuitem(key, value)
            self._menu.addItem_(value._menuitem)
            if self._is_view_based_menuitem(value):
                self._set_subview_dimensions(self, value)
            super(Menu, self).__setitem__(key, value)

    def __delitem__(self, key):
        value = self[key]
        self._menu.removeItem_(value._menuitem)
        super(Menu, self).__delitem__(key)

    def add(self, menuitem):
        """
        Adds the object to the menu as a MenuItem using the MenuItem.title as the key.
        menuitem will be converted to a MenuItem object if not one already.
        """
        self.__setitem__(self._choose_key, menuitem)

    def clear(self):
        """Remove all MenuItem objects from within the menu of this MenuItem."""
        self._menu.removeAllItems()
        super(Menu, self).clear()

    def copy(self):
        raise NotImplementedError

    @classmethod
    def fromkeys(cls, *args, **kwargs):
        raise NotImplementedError

    def _set_subview_dimensions(self, menu, ele):
        """Ensure the item view spans the full width of the menu."""
        menu_width = max(menu._menu.size().width, 200)
        view = ele._menuitem.view()
        if not view:
            return  # No view to resize

        view_height = view.frame().size.height
        view.setFrameSize_((menu_width, view_height))

        # Give the subview (e.g. slider) 5% padding on each side
        # Check if there are subviews before accessing them
        subviews = view.subviews()
        if subviews and len(subviews) > 0:
            subview = subviews[0]
            subview.setFrame_(AppKit.NSMakeRect(
                (menu_width - menu_width * 0.9) / 2,
                (view_height - view_height * 0.9) / 2,
                menu_width * 0.9,
                view_height * 0.9
            ))

    def _is_view_based_menuitem(self, value):
        """Check if the value is a view-based menu item."""
        from .slider import SliderMenuItem
        from .textfield import TextFieldMenuItem
        from .image import ImageMenuItem
        from .list import ListMenuItem, ListView
        from .card import CardMenuItem
        return isinstance(value, (SliderMenuItem, TextFieldMenuItem, ImageMenuItem, ListMenuItem, ListView, CardMenuItem))

    def update(self, iterable, **kwargs):
        """
        Update with objects from iterable after each is converted to a MenuItem, ignoring existing keys.

        This update is a bit different from the usual dict.update method. It works recursively and
        will parse a variety of Python containers and objects, creating MenuItem objects and submenus as necessary.

        If the iterable is an instance of MenuItem, then add to the menu.

        Otherwise, for each element in the iterable:
        - if the element is a string or is not an iterable itself, it will be converted to a MenuItem
          and the key will be its string representation.
        - if the element is a MenuItem already, it will remain the same and the key will be its title attribute.
        - if the element is an iterable having a length of 2, the first value will be converted to a MenuItem
          and the second will act as the submenu for that MenuItem.
        - if the element is an iterable having a length of anything other than 2, a ValueError will be raised.
        - if the element is a mapping, each key-value pair will act as an iterable having a length of 2.
        """
        def parse_menu(iterable, menu, depth):
            from .standard import MenuItem

            if isinstance(iterable, MenuItem):
                menu.add(iterable)
                return

            for n, ele in enumerate(iteritems(iterable) if isinstance(iterable, collections_abc.Mapping) else iterable):

                # for mappings we recurse but don't drop down a level in the menu
                if not isinstance(ele, MenuItem) and isinstance(ele, collections_abc.Mapping):
                    parse_menu(ele, menu, depth)

                # any iterables other than strings and MenuItems
                elif not isinstance(ele, (string_types, MenuItem)) and isinstance(ele, collections_abc.Iterable):
                    try:
                        menuitem, submenu = ele
                    except TypeError:
                        raise ValueError('menu iterable element #{0} at depth {1} has length {2}; must be a single '
                                       'menu item or a pair consisting of a menu item and its '
                                       'submenu'.format(n, depth, len(tuple(ele))))
                    menuitem = MenuItem(menuitem)
                    menu.add(menuitem)
                    parse_menu(submenu, menuitem, depth+1)

                # menu item / could be visual separator where ele is None or separator
                else:
                    menu.add(ele)
                    if self._is_view_based_menuitem(ele):
                        self._set_subview_dimensions(menu, ele)

        parse_menu(iterable, self, 0)
        parse_menu(kwargs, self, 0)

    # ListDict insertion methods
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def insert_after(self, existing_key, menuitem):
        """
        Insert a MenuItem in the menu after the existing_key.

        :param existing_key: a string key for an existing MenuItem value.
        :param menuitem: an object to be added. It will be converted to a MenuItem if not one already.
        """
        key, menuitem = self._process_new_menuitem(self._choose_key, menuitem)
        self._insert_helper(existing_key, key, menuitem, 1)
        super(Menu, self).insert_after(existing_key, (key, menuitem))

    def insert_before(self, existing_key, menuitem):
        """
        Insert a MenuItem in the menu before the existing_key.

        :param existing_key: a string key for an existing MenuItem value.
        :param menuitem: an object to be added. It will be converted to a MenuItem if not one already.
        """
        key, menuitem = self._process_new_menuitem(self._choose_key, menuitem)
        self._insert_helper(existing_key, key, menuitem, 0)
        super(Menu, self).insert_before(existing_key, (key, menuitem))

    def _insert_helper(self, existing_key, key, menuitem, pos):
        if existing_key == key:
            raise ValueError('same key provided for location and insertion')
        existing_menuitem = self[existing_key]
        index = self._menu.indexOfItem_(existing_menuitem._menuitem)
        self._menu.insertItem_atIndex_(menuitem._menuitem, index + pos)
        if self._is_view_based_menuitem(menuitem):
            self._set_subview_dimensions(self, menuitem)

    # Processing MenuItems
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _process_new_menuitem(self, key, value):
        from .standard import MenuItem
        from .separator import separator
        # During transition, use the original SeparatorMenuItem from rumps.py
        from rumps.rumps import SeparatorMenuItem

        if value is None or value is separator:
            value = SeparatorMenuItem()

        if not hasattr(value, '_menuitem'):
            value = MenuItem(value)

        if key is self._choose_key:
            if hasattr(value, 'title'):
                key = value.title
            else:
                cls = type(value)
                count = self._counts[cls] = self._counts.get(cls, 0) + 1
                key = '%s_%d' % (cls.__name__, count)

        if hasattr(value, 'title') and key != value.title:
            _log('WARNING: key {0} is not the same as the title of the corresponding MenuItem {1}; while this '
                 'would occur if the title is dynamically altered, having different names at the time of menu '
                 'creation may not be desired '.format(repr(key), repr(value.title)))

        return key, value
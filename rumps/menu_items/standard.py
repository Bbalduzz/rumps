#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Standard MenuItem class for rumps."""

from AppKit import NSMenuItem, NSMenu, NSApp

from .base import BaseMenuItem
from .menu import Menu
from ..utils.helpers import nsimage_from_file, _log
from ..utils.internal import require_string_or_none
from ..utils.compat import text_type


class MenuItem(BaseMenuItem, Menu):
    """
    Represents an item within the application's menu.

    A MenuItem is a button inside a menu but it can also serve as a menu itself whose elements are
    other MenuItem instances.

    Encapsulates and abstracts Objective-C NSMenuItem (and possibly a corresponding NSMenu as a submenu).

    A couple of important notes:
    - A new MenuItem instance can be created from any object with a string representation.
    - Attempting to create a MenuItem by passing an existing MenuItem instance as the first parameter will not
      result in a new instance but will instead return the existing instance.

    Remembers the order of items added to menu and has constant time lookup. Can insert new MenuItem object before or
    after other specified ones.

    Note: When adding a MenuItem instance to a menu, the value of title at that time will serve as its key for
    lookup performed on menus even if the title changes during program execution.
    """

    # NOTE:
    # Because of the quirks of PyObjC, a class level dictionary **inside an NSObject subclass for 10.9.x** is required
    # in order to have callback_ be a @classmethod. And we need callback_ to be class level because we can't use
    # instances in setTarget_ method of NSMenuItem. Otherwise this would be much more straightforward like Timer class.
    #
    # So the target is always the NSApp class and action is always the @classmethod callback_ -- for every function
    # decorated with @clicked(...). All we do is lookup the MenuItem instance and the user-provided callback function
    # based on the NSMenuItem (the only argument passed to callback_).

    def __new__(cls, *args, **kwargs):
        if args and isinstance(args[0], MenuItem):
            return args[0]
        return super(MenuItem, cls).__new__(cls, *args, **kwargs)

    def __init__(self, title, callback=None, key=None, icon=None, dimensions=None, template=None):
        if isinstance(title, MenuItem):
            return
        BaseMenuItem.__init__(self)
        self._menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(text_type(title), None, '')
        self._menuitem.setTarget_(NSApp)
        self._menu = self._icon = None
        self.set_callback(callback, key)
        self._template = template
        self.set_icon(icon, dimensions, template)
        Menu.__init__(self)

    def __setitem__(self, key, value):
        if self._menu is None:
            self._menu = NSMenu.alloc().init()
            self._menuitem.setSubmenu_(self._menu)
        super(MenuItem, self).__setitem__(key, value)

    def __repr__(self):
        return '<{0}: [{1} -> {2}; callback: {3}]>'.format(
            type(self).__name__,
            repr(self.title),
            list(map(str, self)),
            repr(self.callback)
        )

    @property
    def title(self):
        """The text displayed in a menu for this menu item. If not a string, will use the string representation."""
        return self._menuitem.title()

    @title.setter
    def title(self, new_title):
        new_title = text_type(new_title)
        self._menuitem.setTitle_(new_title)

    @property
    def icon(self):
        """
        The path to an image displayed next to the text for this menu item.
        If set to None, the current image (if any) is removed.
        """
        return self._icon

    @icon.setter
    def icon(self, icon_path):
        self.set_icon(icon_path, template=self._template)

    @property
    def template(self):
        """
        Template mode for an icon. If set to None, the current icon (if any) is displayed as a color icon.
        If set to True, template mode is enabled and the icon will be displayed correctly in dark menu bar mode.
        """
        return self._template

    @template.setter
    def template(self, template_mode):
        self._template = template_mode
        self.set_icon(self.icon, template=template_mode)

    def set_icon(self, icon_path, dimensions=None, template=None):
        """
        Sets the icon displayed next to the text for this menu item.
        If set to None, the current image (if any) is removed. Can optionally supply dimensions.

        :param icon_path: a file path to an image.
        :param dimensions: a sequence of numbers whose length is two.
        :param template: a boolean who defines the template mode for the icon.
        """
        new_icon = nsimage_from_file(icon_path, dimensions, template) if icon_path is not None else None
        self._icon = icon_path
        self._menuitem.setImage_(new_icon)

    @property
    def state(self):
        """
        The state of the menu item. The "on" state is symbolized by a check mark. The "mixed" state is symbolized
        by a dash.

        State  Number
        =====  ======
         ON      1
         OFF     0
        MIXED   -1
        =====  ======
        """
        return self._menuitem.state()

    @state.setter
    def state(self, new_state):
        self._menuitem.setState_(new_state)

    def set_callback(self, callback, key=None):
        """
        Set the function serving as callback for when a click event occurs on this menu item.
        When callback is None, it will disable the callback function and grey out the menu item.
        If key is a string, set as the key shortcut. If it is None, no adjustment will be made to the current key shortcut.

        :param callback: the function to be called when the user clicks on this menu item.
        :param key: the key shortcut to click this menu item.
        """
        require_string_or_none(key)
        if key is not None:
            self._menuitem.setKeyEquivalent_(key)

        # During transition, handle NSApp not being initialized yet
        try:
            # Check if NSApp has the callback dictionary
            if not hasattr(NSApp, '_ns_to_py_and_callback'):
                # Can't set attributes on NSApp if it's None, will be set up by App class
                pass
            else:
                NSApp._ns_to_py_and_callback[self._menuitem] = self, callback
        except AttributeError:
            # NSApp not properly initialized yet, skip for now
            pass

        self._menuitem.setAction_('callback:' if callback is not None else None)

    @property
    def callback(self):
        """Return the current callback function."""
        if hasattr(NSApp, '_ns_to_py_and_callback'):
            return NSApp._ns_to_py_and_callback.get(self._menuitem, (None, None))[1]
        return None

    @property
    def values(self):
        """Return values in the order they were added to the menu."""
        return list(super(MenuItem, self).values())
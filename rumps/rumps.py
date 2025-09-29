# -*- coding: utf-8 -*-

# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.


# For compatibility with pyinstaller
# See: http://stackoverflow.com/questions/21058889/pyinstaller-not-finding-pyobjc-library-macos-python
import Foundation
import AppKit

from Foundation import (NSDate, NSTimer, NSRunLoop, NSDefaultRunLoopMode, NSSearchPathForDirectoriesInDomains,
                        NSMakeRect, NSLog, NSObject, NSMutableDictionary, NSString, NSUserDefaults)
from AppKit import NSApplication, NSStatusBar, NSMenu, NSMenuItem, NSAlert, NSTextField, NSSecureTextField, NSImage, NSSlider, NSSize, NSWorkspace, NSWorkspaceWillSleepNotification, NSWorkspaceDidWakeNotification, NSView
from PyObjCTools import AppHelper

import os
import pickle
import traceback
import weakref

from .compat import text_type, string_types, iteritems, collections_abc
from .text_field import Editing, SecureEditing
from .utils import ListDict

from . import _internal
from . import events
from . import notifications

_TIMERS = weakref.WeakKeyDictionary()
separator = object()


def debug_mode(choice):
    """Enable/disable printing helpful information for debugging the program. Default is off."""
    global _log
    if choice:
        def _log(*args):
            NSLog(' '.join(map(str, args)))
    else:
        def _log(*_):
            pass
debug_mode(False)


def alert(title=None, message='', ok=None, cancel=None, other=None, icon_path=None):
    """Generate a simple alert window.

    .. versionchanged:: 0.2.0
        Providing a `cancel` string will set the button text rather than only using text "Cancel". `title` is no longer
        a required parameter.

    .. versionchanged:: 0.3.0
        Add `other` button functionality as well as `icon_path` to change the alert icon.

    :param title: the text positioned at the top of the window in larger font. If ``None``, a default localized title
                  is used. If not ``None`` or a string, will use the string representation of the object.
    :param message: the text positioned below the `title` in smaller font. If not a string, will use the string
                    representation of the object.
    :param ok: the text for the "ok" button. Must be either a string or ``None``. If ``None``, a default
               localized button title will be used.
    :param cancel: the text for the "cancel" button. If a string, the button will have that text. If `cancel`
                   evaluates to ``True``, will create a button with text "Cancel". Otherwise, this button will not be
                   created.
    :param other: the text for the "other" button. If a string, the button will have that text. Otherwise, this button will not be
                   created.
    :param icon_path: a path to an image. If ``None``, the applications icon is used.
    :return: a number representing the button pressed. The "ok" button is ``1`` and "cancel" is ``0``.
    """
    message = text_type(message)
    message = message.replace('%', '%%')
    if title is not None:
        title = text_type(title)
    _internal.require_string_or_none(ok)
    if not isinstance(cancel, string_types):
        cancel = 'Cancel' if cancel else None
    alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
        title, ok, cancel, other, message)
    if NSUserDefaults.standardUserDefaults().stringForKey_('AppleInterfaceStyle') == 'Dark':
        alert.window().setAppearance_(AppKit.NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark'))
    alert.setAlertStyle_(0)  # informational style
    if icon_path is not None:
        icon = _nsimage_from_file(icon_path)
        alert.setIcon_(icon)
    _log('alert opened with message: {0}, title: {1}'.format(repr(message), repr(title)))
    return alert.runModal()


def application_support(name):
    """Return the application support folder path for the given `name`, creating it if it doesn't exist."""
    app_support_path = os.path.join(NSSearchPathForDirectoriesInDomains(14, 1, 1).objectAtIndex_(0), name)
    if not os.path.isdir(app_support_path):
        os.mkdir(app_support_path)
    return app_support_path


def timers():
    """Return a list of all :class:`rumps.Timer` objects. These can be active or inactive."""
    return list(_TIMERS)


def quit_application(sender=None):
    """Quit the application. Some menu item should call this function so that the application can exit gracefully."""
    nsapplication = NSApplication.sharedApplication()
    _log('closing application')
    nsapplication.terminate_(sender)


def _nsimage_from_file(filename, dimensions=None, template=None):
    """Take a path to an image file and return an NSImage object."""
    try:
        _log('attempting to open image at {0}'.format(filename))
        with open(filename):
            pass
    except IOError:  # literal file path didn't work -- try to locate image based on main script path
        try:
            from __main__ import __file__ as main_script_path
            main_script_path = os.path.dirname(main_script_path)
            filename = os.path.join(main_script_path, filename)
        except ImportError:
            pass
        _log('attempting (again) to open image at {0}'.format(filename))
        with open(filename):  # file doesn't exist
            pass              # otherwise silently errors in NSImage which isn't helpful for debugging
    image = NSImage.alloc().initByReferencingFile_(filename)
    image.setScalesWhenResized_(True)
    image.setSize_((20, 20) if dimensions is None else dimensions)
    if not template is None:
        image.setTemplate_(template)
    return image


# Decorators and helper function serving to register functions for dealing with interaction and events
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def timer(interval):
    """Decorator for registering a function as a callback in a new thread. The function will be repeatedly called every
    `interval` seconds. This decorator accomplishes the same thing as creating a :class:`rumps.Timer` object by using
    the decorated function and `interval` as parameters and starting it on application launch.

    .. code-block:: python

        @rumps.timer(2)
        def repeating_function(sender):
            print 'hi'

    :param interval: a number representing the time in seconds before the decorated function should be called.
    """
    def decorator(f):
        timers = timer.__dict__.setdefault('*timers', [])
        timers.append(Timer(f, interval))
        return f
    return decorator


def clicked(*args, **options):
    """Decorator for registering a function as a callback for a click action on a :class:`rumps.MenuItem` within the
    application. The passed `args` must specify an existing path in the main menu. The :class:`rumps.MenuItem`
    instance at the end of that path will have its :meth:`rumps.MenuItem.set_callback` method called, passing in the
    decorated function.

    .. versionchanged:: 0.2.1
        Accepts `key` keyword argument.

    .. code-block:: python

        @rumps.clicked('Animal', 'Dog', 'Corgi')
        def corgi_button(sender):
            import subprocess
            subprocess.call(['say', '"corgis are the cutest"'])

    :param args: a series of strings representing the path to a :class:`rumps.MenuItem` in the main menu of the
                 application.
    :param key: a string representing the key shortcut as an alternative means of clicking the menu item.
    """
    def decorator(f):

        def register_click(self):
            menuitem = self._menu  # self not defined yet but will be later in 'run' method
            if menuitem is None:
                raise ValueError('no menu created')
            for arg in args:
                try:
                    menuitem = menuitem[arg]
                except KeyError:
                    menuitem.add(arg)
                    menuitem = menuitem[arg]
            menuitem.set_callback(f, options.get('key'))

        # delay registering the button until we have a current instance to be able to traverse the menu
        buttons = clicked.__dict__.setdefault('*buttons', [])
        buttons.append(register_click)

        return f
    return decorator


def slider(*args, **options):
    """Decorator for registering a function as a callback for a slide action on a :class:`rumps.SliderMenuItem` within
    the application. All elements of the provided path will be created as :class:`rumps.MenuItem` objects. The
    :class:`rumps.SliderMenuItem` will be created as a child of the last menu item.

    Accepts the same keyword arguments as :class:`rumps.SliderMenuItem`.

    .. versionadded:: 0.3.0

    :param args: a series of strings representing the path to a :class:`rumps.SliderMenuItem` in the main menu of the
                 application.
    """
    def decorator(f):

        def register_click(self):

            # self not defined yet but will be later in 'run' method
            menuitem = self._menu
            if menuitem is None:
                raise ValueError('no menu created')

            # create here in case of error so we don't create the path
            slider_menu_item = SliderMenuItem(**options)
            slider_menu_item.set_callback(f)

            for arg in args:
                try:
                    menuitem = menuitem[arg]
                except KeyError:
                    menuitem.add(arg)
                    menuitem = menuitem[arg]

            menuitem.add(slider_menu_item)

        # delay registering the button until we have a current instance to be able to traverse the menu
        buttons = clicked.__dict__.setdefault('*buttons', [])
        buttons.append(register_click)

        return f
    return decorator


def textfield(*args, **options):
    """Decorator for registering a function as a callback for a text change action on a :class:`rumps.TextFieldMenuItem` within
    the application. All elements of the provided path will be created as :class:`rumps.MenuItem` objects. The
    :class:`rumps.TextFieldMenuItem` will be created as a child of the last menu item.

    Accepts the same keyword arguments as :class:`rumps.TextFieldMenuItem`.

    :param args: a series of strings representing the path to a :class:`rumps.TextFieldMenuItem` in the main menu of the
                 application.
    """
    def decorator(f):

        def register_textfield(self):

            # self not defined yet but will be later in 'run' method
            menuitem = self._menu
            if menuitem is None:
                raise ValueError('no menu created')

            # create here in case of error so we don't create the path
            textfield_menu_item = TextFieldMenuItem(**options)
            textfield_menu_item.set_callback(f)

            for arg in args:
                try:
                    menuitem = menuitem[arg]
                except KeyError:
                    menuitem.add(arg)
                    menuitem = menuitem[arg]

            menuitem.add(textfield_menu_item)

        # delay registering the textfield until we have a current instance to be able to traverse the menu
        buttons = clicked.__dict__.setdefault('*buttons', [])
        buttons.append(register_textfield)

        return f
    return decorator


def image(*args, **options):
    """Decorator for registering a function as a callback for an image click action on a :class:`rumps.ImageMenuItem` within
    the application. All elements of the provided path will be created as :class:`rumps.MenuItem` objects. The
    :class:`rumps.ImageMenuItem` will be created as a child of the last menu item.

    Accepts the same keyword arguments as :class:`rumps.ImageMenuItem`.

    :param args: a series of strings representing the path to a :class:`rumps.ImageMenuItem` in the main menu of the
                 application.
    """
    def decorator(f):

        def register_image(self):

            # self not defined yet but will be later in 'run' method
            menuitem = self._menu
            if menuitem is None:
                raise ValueError('no menu created')

            # create here in case of error so we don't create the path
            image_menu_item = ImageMenuItem(**options)
            image_menu_item.set_callback(f)

            for arg in args:
                try:
                    menuitem = menuitem[arg]
                except KeyError:
                    menuitem.add(arg)
                    menuitem = menuitem[arg]

            menuitem.add(image_menu_item)

        # delay registering the image until we have a current instance to be able to traverse the menu
        buttons = clicked.__dict__.setdefault('*buttons', [])
        buttons.append(register_image)

        return f
    return decorator


def list_menu(*args, **options):
    """Decorator for registering a function as a callback for a list selection action on a :class:`rumps.ListMenuItem` within
    the application. All elements of the provided path will be created as :class:`rumps.MenuItem` objects. The
    :class:`rumps.ListMenuItem` will be created as a child of the last menu item.

    Accepts the same keyword arguments as :class:`rumps.ListMenuItem`.

    :param args: a series of strings representing the path to a :class:`rumps.ListMenuItem` in the main menu of the
                 application.
    """
    def decorator(f):

        def register_list(self):

            # self not defined yet but will be later in 'run' method
            menuitem = self._menu
            if menuitem is None:
                raise ValueError('no menu created')

            # create here in case of error so we don't create the path
            list_menu_item = ListMenuItem(**options)
            list_menu_item.set_callback(f)

            for arg in args:
                try:
                    menuitem = menuitem[arg]
                except KeyError:
                    menuitem.add(arg)
                    menuitem = menuitem[arg]

            menuitem.add(list_menu_item)

        # delay registering the list until we have a current instance to be able to traverse the menu
        buttons = clicked.__dict__.setdefault('*buttons', [])
        buttons.append(register_list)

        return f
    return decorator


def card(*args, **options):
    """Decorator for registering a function as a callback for a card click action on a :class:`rumps.CardMenuItem` within
    the application. All elements of the provided path will be created as :class:`rumps.MenuItem` objects. The
    :class:`rumps.CardMenuItem` will be created as a child of the last menu item.

    Accepts the same keyword arguments as :class:`rumps.CardMenuItem`.

    :param args: a series of strings representing the path to a :class:`rumps.CardMenuItem` in the main menu of the
                 application.
    """
    def decorator(f):

        def register_card(self):

            # self not defined yet but will be later in 'run' method
            menuitem = self._menu
            if menuitem is None:
                raise ValueError('no menu created')

            # create here in case of error so we don't create the path
            card_menu_item = CardMenuItem(**options)
            card_menu_item.set_callback(f)

            for arg in args:
                try:
                    menuitem = menuitem[arg]
                except KeyError:
                    menuitem.add(arg)
                    menuitem = menuitem[arg]

            menuitem.add(card_menu_item)

        # delay registering the card until we have a current instance to be able to traverse the menu
        buttons = clicked.__dict__.setdefault('*buttons', [])
        buttons.append(register_card)

        return f
    return decorator

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class Menu(ListDict):
    """Wrapper for Objective-C's NSMenu class.

    Implements core functionality of menus in rumps. :class:`rumps.MenuItem` subclasses `Menu`.
    """

    # NOTE:
    # Only ever used as the main menu since every other menu would exist as a submenu of a MenuItem

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
            if isinstance(value, (SliderMenuItem, TextFieldMenuItem, ImageMenuItem, ListMenuItem, ListView, CardMenuItem)):
                self._set_subview_dimensions(self, value)
            super(Menu, self).__setitem__(key, value)

    def __delitem__(self, key):
        value = self[key]
        self._menu.removeItem_(value._menuitem)
        super(Menu, self).__delitem__(key)

    def add(self, menuitem):
        """Adds the object to the menu as a :class:`rumps.MenuItem` using the :attr:`rumps.MenuItem.title` as the
        key. `menuitem` will be converted to a `MenuItem` object if not one already.
        """
        self.__setitem__(self._choose_key, menuitem)

    def clear(self):
        """Remove all `MenuItem` objects from within the menu of this `MenuItem`."""
        self._menu.removeAllItems()
        super(Menu, self).clear()

    def copy(self):
        raise NotImplementedError

    @classmethod
    def fromkeys(cls, *args, **kwargs):
        raise NotImplementedError

    def _set_subview_dimensions(self, menu, ele):
            # Ensure the item view spans the full width of the menu
            menu_width = max(menu._menu.size().width, 200)
            view = ele._menuitem.view()
            view_height = view.frame().size.height
            view.setFrameSize_((menu_width, view_height))

            # Give the subview (e.g. slider) 5% padding on each side
            subview = view.subviews()[0]
            subview.setFrame_(AppKit.NSMakeRect((menu_width - menu_width * 0.9) / 2, (view_height - view_height * 0.9) / 2, menu_width * 0.9, view_height * 0.9))

    def update(self, iterable, **kwargs):
        """Update with objects from `iterable` after each is converted to a :class:`rumps.MenuItem`, ignoring
        existing keys. This update is a bit different from the usual ``dict.update`` method. It works recursively and
        will parse a variety of Python containers and objects, creating `MenuItem` object and submenus as necessary.

        If the `iterable` is an instance of :class:`rumps.MenuItem`, then add to the menu.

        Otherwise, for each element in the `iterable`,

            - if the element is a string or is not an iterable itself, it will be converted to a
              :class:`rumps.MenuItem` and the key will be its string representation.
            - if the element is a :class:`rumps.MenuItem` already, it will remain the same and the key will be its
              :attr:`rumps.MenuItem.title` attribute.
            - if the element is an iterable having a length of 2, the first value will be converted to a
              :class:`rumps.MenuItem` and the second will act as the submenu for that `MenuItem`
            - if the element is an iterable having a length of anything other than 2, a ``ValueError`` will be raised
            - if the element is a mapping, each key-value pair will act as an iterable having a length of 2

        """
        def parse_menu(iterable, menu, depth):
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
                    if isinstance(ele, (SliderMenuItem, TextFieldMenuItem, ImageMenuItem, ListMenuItem, ListView, CardMenuItem)):
                        self._set_subview_dimensions(menu, ele)
        parse_menu(iterable, self, 0)
        parse_menu(kwargs, self, 0)

    # ListDict insertion methods
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def insert_after(self, existing_key, menuitem):
        """Insert a :class:`rumps.MenuItem` in the menu after the `existing_key`.

        :param existing_key: a string key for an existing `MenuItem` value.
        :param menuitem: an object to be added. It will be converted to a `MenuItem` if not one already.
        """
        key, menuitem = self._process_new_menuitem(self._choose_key, menuitem)
        self._insert_helper(existing_key, key, menuitem, 1)
        super(Menu, self).insert_after(existing_key, (key, menuitem))

    def insert_before(self, existing_key, menuitem):
        """Insert a :class:`rumps.MenuItem` in the menu before the `existing_key`.

        :param existing_key: a string key for an existing `MenuItem` value.
        :param menuitem: an object to be added. It will be converted to a `MenuItem` if not one already.
        """
        key, menuitem = self._process_new_menuitem(self._choose_key, menuitem)
        self._insert_helper(existing_key, key, menuitem, 0)
        super(Menu, self).insert_before(existing_key, (key, menuitem))

    def _insert_helper(self, existing_key, key, menuitem, pos):
        if existing_key == key:  # this would mess stuff up...
            raise ValueError('same key provided for location and insertion')
        existing_menuitem = self[existing_key]
        index = self._menu.indexOfItem_(existing_menuitem._menuitem)
        self._menu.insertItem_atIndex_(menuitem._menuitem, index + pos)
        if isinstance(menuitem, (SliderMenuItem, TextFieldMenuItem, ImageMenuItem, ListMenuItem, ListView, CardMenuItem)):
            self._set_subview_dimensions(self, menuitem)

    # Processing MenuItems
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _process_new_menuitem(self, key, value):
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


class MenuItem(Menu):
    """Represents an item within the application's menu.

    A :class:`rumps.MenuItem` is a button inside a menu but it can also serve as a menu itself whose elements are
    other `MenuItem` instances.

    Encapsulates and abstracts Objective-C NSMenuItem (and possibly a corresponding NSMenu as a submenu).

    A couple of important notes:

        - A new `MenuItem` instance can be created from any object with a string representation.
        - Attempting to create a `MenuItem` by passing an existing `MenuItem` instance as the first parameter will not
          result in a new instance but will instead return the existing instance.

    Remembers the order of items added to menu and has constant time lookup. Can insert new `MenuItem` object before or
    after other specified ones.

    .. note::
       When adding a `MenuItem` instance to a menu, the value of :attr:`title` at that time will serve as its key for
       lookup performed on menus even if the `title` changes during program execution.

    :param title: the name of this menu item. If not a string, will use the string representation of the object.
    :param callback: the function serving as callback for when a click event occurs on this menu item.
    :param key: the key shortcut to click this menu item. Must be a string or ``None``.
    :param icon: a path to an image. If set to ``None``, the current image (if any) is removed.
    :param dimensions: a sequence of numbers whose length is two, specifying the dimensions of the icon.
    :param template: a boolean, specifying template mode for a given icon (proper b/w display in dark menu bar)
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
        if args and isinstance(args[0], MenuItem):  # can safely wrap MenuItem instances
            return args[0]
        return super(MenuItem, cls).__new__(cls, *args, **kwargs)

    def __init__(self, title, callback=None, key=None, icon=None, dimensions=None, template=None):
        if isinstance(title, MenuItem):  # don't initialize already existing instances
            return
        self._menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(text_type(title), None, '')
        self._menuitem.setTarget_(NSApp)
        self._menu = self._icon = None
        self.set_callback(callback, key)
        self._template = template
        self.set_icon(icon, dimensions, template)
        super(MenuItem, self).__init__()

    def __setitem__(self, key, value):
        if self._menu is None:
            self._menu = NSMenu.alloc().init()
            self._menuitem.setSubmenu_(self._menu)
        super(MenuItem, self).__setitem__(key, value)

    def __repr__(self):
        return '<{0}: [{1} -> {2}; callback: {3}]>'.format(type(self).__name__, repr(self.title), list(map(str, self)),
                                                           repr(self.callback))

    @property
    def title(self):
        """The text displayed in a menu for this menu item. If not a string, will use the string representation of the
        object.
        """
        return self._menuitem.title()

    @title.setter
    def title(self, new_title):
        new_title = text_type(new_title)
        self._menuitem.setTitle_(new_title)

    @property
    def icon(self):
        """The path to an image displayed next to the text for this menu item. If set to ``None``, the current image
        (if any) is removed.

        .. versionchanged:: 0.2.0
           Setting icon to ``None`` after setting it to an image will correctly remove the icon. Returns the path to an
           image rather than exposing a `PyObjC` class.

        """
        return self._icon

    @icon.setter
    def icon(self, icon_path):
        self.set_icon(icon_path, template=self._template)

    @property
    def template(self):
        """Template mode for an icon. If set to ``None``, the current icon (if any) is displayed as a color icon.
        If set to ``True``, template mode is enabled and the icon will be displayed correctly in dark menu bar mode.
        """
        return self._template

    @template.setter
    def template(self, template_mode):
        self._template = template_mode
        self.set_icon(self.icon, template=template_mode)

    def set_icon(self, icon_path, dimensions=None, template=None):
        """Sets the icon displayed next to the text for this menu item. If set to ``None``, the current image (if any)
        is removed. Can optionally supply `dimensions`.

        .. versionchanged:: 0.2.0
           Setting `icon` to ``None`` after setting it to an image will correctly remove the icon. Passing `dimensions`
           a sequence whose length is not two will no longer silently error.

        :param icon_path: a file path to an image.
        :param dimensions: a sequence of numbers whose length is two.
        :param template: a boolean who defines the template mode for the icon.
        """
        new_icon = _nsimage_from_file(icon_path, dimensions, template) if icon_path is not None else None
        self._icon = icon_path
        self._menuitem.setImage_(new_icon)

    @property
    def state(self):
        """The state of the menu item. The "on" state is symbolized by a check mark. The "mixed" state is symbolized
        by a dash.

        .. table:: Setting states

           =====  ======
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

    @property
    def hidden(self):
        """Indicates whether the menu item is hidden.

        .. versionadded:: 0.4.0

        """
        return self._menuitem.isHidden()

    @hidden.setter
    def hidden(self, value):
        self._menuitem.setHidden_(value)

    def hide(self):
        """Hide the menu item.

        .. versionadded:: 0.4.0

        """
        self.hidden = True

    def show(self):
        """Show the menu item.

        .. versionadded:: 0.4.0

        """
        self.hidden = False

    def set_callback(self, callback, key=None):
        """Set the function serving as callback for when a click event occurs on this menu item. When `callback` is
        ``None``, it will disable the callback function and grey out the menu item. If `key` is a string, set as the
        key shortcut. If it is ``None``, no adjustment will be made to the current key shortcut.

        .. versionchanged:: 0.2.0
           Allowed passing ``None`` as both `callback` and `key`. Additionally, passing a `key` that is neither a
           string nor ``None`` will result in a standard ``TypeError`` rather than various, uninformative `PyObjC`
           internal errors depending on the object.

        :param callback: the function to be called when the user clicks on this menu item.
        :param key: the key shortcut to click this menu item.
        """
        _internal.require_string_or_none(key)
        if key is not None:
            self._menuitem.setKeyEquivalent_(key)
        NSApp._ns_to_py_and_callback[self._menuitem] = self, callback
        self._menuitem.setAction_('callback:' if callback is not None else None)

    @property
    def callback(self):
        """Return the current callback function.

        .. versionadded:: 0.2.0

        """
        return NSApp._ns_to_py_and_callback[self._menuitem][1]

    @property
    def key(self):
        """The key shortcut to click this menu item.

        .. versionadded:: 0.2.0

        """
        return self._menuitem.keyEquivalent()


class SliderMenuItem(object):
    """Represents a slider menu item within the application's menu.

    .. versionadded:: 0.3.0

    :param value: a number for the current position of the slider.
    :param min_value: a number for the minimum position to which a slider can be moved.
    :param max_value: a number for the maximum position to which a slider can be moved.
    :param callback: the function serving as callback for when a slide event occurs on this menu item.
    :param dimensions: a sequence of numbers whose length is two, specifying the dimensions of the slider.
    """

    def __init__(self, value=50, min_value=0, max_value=100, callback=None, dimensions=(180, 15)):
        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 0, 30))
        self._slider = NSSlider.alloc().init()
        self._slider.setMinValue_(min_value)
        self._slider.setMaxValue_(max_value)
        self._slider.setDoubleValue_(value)
        self._slider.setFrameSize_(NSSize(*dimensions))
        self._slider.setTarget_(NSApp)
        self._menuitem = NSMenuItem.alloc().init()
        self._menuitem.setTarget_(NSApp)
        self._view.addSubview_(self._slider)
        self._menuitem.setView_(self._view)
        self.set_callback(callback)

    def __repr__(self):
        return '<{0}: [value: {1}; callback: {2}]>'.format(
            type(self).__name__,
            self.value,
            repr(self.callback)
        )

    def set_callback(self, callback):
        """Set the function serving as callback for when a slide event occurs on this menu item.

        :param callback: the function to be called when the user drags the marker on the slider.
        """
        NSApp._ns_to_py_and_callback[self._slider] = self, callback
        self._slider.setAction_('callback:' if callback is not None else None)

    @property
    def callback(self):
        return NSApp._ns_to_py_and_callback[self._slider][1]

    @property
    def value(self):
        """The current position of the slider."""
        return self._slider.doubleValue()

    @value.setter
    def value(self, new_value):
        self._slider.setDoubleValue_(new_value)


class TextFieldMenuItem(object):
    """Represents a text input field menu item within the application's menu.

    A text field that can be embedded directly in the menu, allowing inline text input
    without the need for modal dialogs.

    :param text: the initial text value for the text field.
    :param placeholder: placeholder text shown when the field is empty.
    :param callback: the function serving as callback for when text changes or Enter is pressed.
    :param dimensions: a sequence of numbers whose length is two, specifying the dimensions of the text field.
    :param secure: whether to use a secure text field (for passwords).
    """

    def __init__(self, text="", placeholder="", callback=None, dimensions=(180, 20), secure=False):
        from .text_field import Editing, SecureEditing

        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 0, 30))

        # Create the appropriate text field type
        if secure:
            self._textfield = SecureEditing.alloc().initWithFrame_(NSMakeRect(0, 0, *dimensions))
        else:
            self._textfield = Editing.alloc().initWithFrame_(NSMakeRect(0, 0, *dimensions))

        # Configure the text field
        self._textfield.setStringValue_(text)
        self._textfield.setEditable_(True)
        self._textfield.setSelectable_(True)

        # Enable rich text editing features
        self._textfield.setImportsGraphics_(False)
        # self._textfield.setRichText_(False)

        if placeholder:
            # Set placeholder using NSAttributedString for better compatibility
            try:
                placeholder_attr = NSString.stringWithString_(placeholder)
                self._textfield.cell().setPlaceholderString_(placeholder_attr)
            except:
                # Fallback for older macOS versions
                pass

        self._textfield.setTarget_(NSApp)
        self._textfield.setAction_('textFieldCallback:')

        # Set up the menu item
        self._menuitem = NSMenuItem.alloc().init()
        self._menuitem.setTarget_(NSApp)
        self._view.addSubview_(self._textfield)
        self._menuitem.setView_(self._view)

        self.set_callback(callback)

    def __repr__(self):
        return '<{0}: [text: {1}; callback: {2}]>'.format(
            type(self).__name__,
            repr(self.text),
            repr(self.callback)
        )

    def set_callback(self, callback):
        """Set the function serving as callback for when text changes or Enter is pressed.

        :param callback: the function to be called when the user types or presses Enter.
        """
        NSApp._ns_to_py_and_callback[self._textfield] = self, callback
        self._textfield.setAction_('textFieldCallback:' if callback is not None else None)

    @property
    def callback(self):
        """Return the current callback function."""
        return NSApp._ns_to_py_and_callback.get(self._textfield, (None, None))[1]

    @property
    def text(self):
        """The current text value of the text field."""
        return self._textfield.stringValue()

    @text.setter
    def text(self, new_text):
        self._textfield.setStringValue_(new_text)

    @property
    def placeholder(self):
        """The placeholder text shown when the field is empty."""
        try:
            return self._textfield.cell().placeholderString()
        except:
            return ""

    @placeholder.setter
    def placeholder(self, new_placeholder):
        try:
            placeholder_attr = NSString.stringWithString_(new_placeholder)
            self._textfield.cell().setPlaceholderString_(placeholder_attr)
        except:
            pass


class ImageMenuItem(object):
    """Represents an image display menu item within the application's menu.

    Displays an image within a menu item, with optional scaling and click callbacks.
    Useful for displaying thumbnails, icons, or visual content directly in menus.

    :param image_path: path to the image file to display.
    :param dimensions: a sequence of numbers whose length is two, specifying the dimensions of the image display.
                      If None, uses the natural dimensions of the loaded image.
    :param callback: the function serving as callback for when the image is clicked.
    :param scale_mode: how to scale the image ('fit', 'fill', 'stretch'). Default is 'fit'.
    :param background_color: background color for the image view (None for transparent).
    """

    def __init__(self, image_path=None, dimensions=None, callback=None, scale_mode='fit', background_color=None):
        from AppKit import NSImageView, NSColor, NSButton

        # Determine dimensions - use image size if not specified
        if dimensions is None and image_path:
            # Load image to get its natural dimensions WITHOUT forcing size
            try:
                # Load image without setting size to get natural dimensions
                temp_image = NSImage.alloc().initByReferencingFile_(image_path)
                if temp_image:
                    image_size = temp_image.size()
                    view_width, view_height = int(image_size.width), int(image_size.height)
                    _log(f'ImageMenuItem: using natural image size {view_width}x{view_height}')
                else:
                    # Fallback if image can't be loaded
                    view_width, view_height = 150, 100
                    _log('ImageMenuItem: failed to load image, using fallback size')
            except Exception as e:
                # Fallback if image can't be loaded
                view_width, view_height = 150, 100
                _log(f'ImageMenuItem: error loading image {e}, using fallback size')
        elif dimensions is None:
            # No image and no dimensions - use default
            view_width, view_height = 150, 100
        else:
            # Use specified dimensions
            view_width, view_height = dimensions

        # Store the final dimensions
        self._dimensions = (view_width, view_height)

        # Create the container view with EXACT sizing (no padding)
        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, view_width, view_height))

        # Create image view with NO padding - fills entire view
        self._image_view = NSImageView.alloc().initWithFrame_(NSMakeRect(0, 0, view_width, view_height))

        # Set scaling mode
        scaling_modes = {
            'fit': 1,      # NSImageScaleProportionallyUpOrDown
            'fill': 0,     # NSImageScaleAxesIndependently
            'stretch': 2   # NSImageScaleNone
        }
        self._image_view.setImageScaling_(scaling_modes.get(scale_mode, 1))

        # Configure image view for better display
        self._image_view.setImageFrameStyle_(0)  # NSImageFrameNone
        self._image_view.setImageAlignment_(4)   # NSImageAlignCenter
        self._image_view.setAnimates_(False)
        self._image_view.setEditable_(False)

        # Set background color if specified
        if background_color:
            if isinstance(background_color, tuple) and len(background_color) >= 3:
                r, g, b = background_color[:3]
                a = background_color[3] if len(background_color) > 3 else 1.0
                color = NSColor.colorWithRed_green_blue_alpha_(r, g, b, a)
                self._image_view.setWantsLayer_(True)
                self._image_view.layer().setBackgroundColor_(color.CGColor())

        # Load and set image
        self._image_path = None
        if image_path:
            self.set_image(image_path)

        # Make it clickable if callback is provided
        if callback:
            # Use a button overlay for click detection - covers entire image
            self._button = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, view_width, view_height))
            self._button.setButtonType_(6)  # NSMomentaryChangeButton
            self._button.setBordered_(False)
            self._button.setTransparent_(True)
            self._button.setTarget_(NSApp)
            self._button.setAction_('imageCallback:')
            self._view.addSubview_(self._button)

        # Set up the menu item
        self._menuitem = NSMenuItem.alloc().init()
        self._menuitem.setTarget_(NSApp)
        self._view.addSubview_(self._image_view)
        self._menuitem.setView_(self._view)

        self.set_callback(callback)

    def __repr__(self):
        return '<{0}: [image: {1}; callback: {2}]>'.format(
            type(self).__name__,
            repr(self._image_path),
            repr(self.callback)
        )

    def set_image(self, image_path):
        """Set the image to display.

        :param image_path: path to the image file, or None to clear the image.
        """
        if image_path is None:
            self._image_view.setImage_(None)
            self._image_path = None
            return

        try:
            # Use _nsimage_from_file with the view dimensions to properly scale
            image = _nsimage_from_file(image_path, dimensions=self._dimensions)
            if image:
                self._image_view.setImage_(image)
                self._image_path = image_path
                _log(f'ImageMenuItem: loaded image from {image_path}')
            else:
                _log(f'ImageMenuItem: failed to load image from {image_path}')
        except Exception as e:
            _log(f'ImageMenuItem: error loading image from {image_path}: {e}')

    def set_callback(self, callback):
        """Set the function serving as callback for when the image is clicked.

        :param callback: the function to be called when the user clicks on the image.
        """
        if hasattr(self, '_button'):
            NSApp._ns_to_py_and_callback[self._button] = self, callback
        else:
            NSApp._ns_to_py_and_callback[self._image_view] = self, callback

    @property
    def callback(self):
        """Return the current callback function."""
        if hasattr(self, '_button'):
            return NSApp._ns_to_py_and_callback.get(self._button, (None, None))[1]
        else:
            return NSApp._ns_to_py_and_callback.get(self._image_view, (None, None))[1]

    @property
    def image_path(self):
        """The path to the currently displayed image."""
        return self._image_path

    @property
    def dimensions(self):
        """The current dimensions of the image view."""
        return self._dimensions


class ListMenuItem(object):
    """Represents a scrollable list menu item within the application's menu.

    Creates a scrollable list of items within a menu, allowing for selection and callbacks.
    Useful for displaying dynamic lists, recent items, or selectable options.

    :param items: list of strings or dictionaries representing list items.
    :param dimensions: a sequence of numbers whose length is two, specifying the dimensions of the list.
    :param callback: the function serving as callback for when an item is selected.
    :param max_visible_items: maximum number of items visible without scrolling.
    :param allow_multiple_selection: whether to allow selecting multiple items.
    """

    def __init__(self, items=None, dimensions=(200, 30), callback=None, max_visible_items=5, allow_multiple_selection=False):
        from AppKit import NSComboBox

        self._items = items or []
        self._selected_index = -1
        self._callback = callback

        # Create the container view
        view_height = max(22, dimensions[1])
        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, dimensions[0], view_height))

        # Create NSComboBox with proper configuration
        self._combo = NSComboBox.alloc().initWithFrame_(NSMakeRect(0, 0, dimensions[0], view_height))

        # Critical configuration for proper appearance and functionality
        self._combo.setUsesDataSource_(False)  # Use simple item management
        self._combo.setCompletes_(False)  # Disable auto-completion
        self._combo.setEditable_(False)  # Make it dropdown-only (not editable)

        # Visual styling
        self._combo.setBordered_(True)
        self._combo.setBezeled_(True)
        self._combo.setDrawsBackground_(True)

        # Interaction settings
        self._combo.setEnabled_(True)
        self._combo.setSelectable_(True)

        # Dropdown behavior
        self._combo.setNumberOfVisibleItems_(min(max_visible_items, 10))

        # Set target and action for selection changes
        # NSComboBox requires notification-based callbacks for selection changes
        self._combo.setTarget_(NSApp)
        self._combo.setAction_('listSelectionCallback:')

        # Also register for selection change notifications
        from Foundation import NSNotificationCenter
        notification_center = NSNotificationCenter.defaultCenter()
        notification_center.addObserver_selector_name_object_(
            NSApp, 'listSelectionCallback:', 'NSComboBoxSelectionDidChangeNotification', self._combo
        )

        # Populate the combo box
        self._update_combo()

        # Set up the menu item
        self._menuitem = NSMenuItem.alloc().init()
        self._menuitem.setTarget_(NSApp)

        # Add combo to view
        self._view.addSubview_(self._combo)
        self._menuitem.setView_(self._view)

        self.set_callback(self._callback)


    def _update_combo(self):
        """Update the combo box with current items."""
        # Clear existing items
        self._combo.removeAllItems()

        if not self._items:
            # Add placeholder if no items
            self._combo.addItemWithObjectValue_("No items")
            self._combo.selectItemAtIndex_(0)
            self._combo.setEnabled_(False)
        else:
            # Add all items
            for item in self._items:
                if isinstance(item, dict):
                    title = item.get('title', str(item))
                else:
                    title = str(item)
                self._combo.addItemWithObjectValue_(title)

            # Enable combo box
            self._combo.setEnabled_(True)

            # Set selection
            if 0 <= self._selected_index < len(self._items):
                self._combo.selectItemAtIndex_(self._selected_index)
            elif self._items:
                self._combo.selectItemAtIndex_(0)
                self._selected_index = 0

    def __repr__(self):
        return '<{0}: [items: {1}; callback: {2}]>'.format(
            type(self).__name__,
            len(self._items),
            repr(self.callback)
        )

    def set_items(self, items):
        """Set the list of items to display.

        :param items: list of strings or dictionaries representing list items.
        """
        self._items = items or []
        self._selected_index = 0 if self._items else -1
        self._update_combo()

    def get_items(self):
        """Get the current list of items."""
        return self._items

    def get_selected_item(self):
        """Get the currently selected item."""
        selected_index = self._combo.indexOfSelectedItem()
        if 0 <= selected_index < len(self._items):
            return self._items[selected_index]
        return None

    def get_selected_index(self):
        """Get the index of the currently selected item."""
        return self._combo.indexOfSelectedItem()

    def set_selected_index(self, index):
        """Set the selected item by index."""
        if 0 <= index < len(self._items):
            self._selected_index = index
            self._combo.selectItemAtIndex_(index)

    def add_item(self, item):
        """Add an item to the list."""
        self._items.append(item)
        if isinstance(item, dict):
            title = item.get('title', str(item))
        else:
            title = str(item)
        self._combo.addItemWithObjectValue_(title)

    def remove_item(self, index):
        """Remove an item from the list by index."""
        if 0 <= index < len(self._items):
            del self._items[index]
            self._combo.removeItemAtIndex_(index)

    def clear_items(self):
        """Remove all items from the list."""
        self._items.clear()
        self._combo.removeAllItems()

    def set_callback(self, callback):
        """Set the function serving as callback for when an item is selected.

        :param callback: the function to be called when an item is selected.
        """
        self._callback = callback
        NSApp._ns_to_py_and_callback[self._combo] = self, callback

    @property
    def callback(self):
        """Return the current callback function."""
        return getattr(self, '_callback', None)

    @property
    def items(self):
        """The current list of items."""
        return self._items

    @items.setter
    def items(self, new_items):
        self.set_items(new_items)


class ListView(object):
    """Represents a scrollable list view within the application's menu.

    Creates a true scrollable list with multiple visible items, allowing for selection and callbacks.
    Different from ListMenuItem (ComboBox) - this shows multiple items at once.

    :param items: list of strings or dictionaries representing list items.
    :param dimensions: a sequence of numbers whose length is two, specifying the dimensions of the list.
    :param callback: the function serving as callback for when an item is selected.
    :param allow_multiple_selection: whether to allow selecting multiple items.
    """

    def __init__(self, items=None, dimensions=(200, 120), callback=None, allow_multiple_selection=False):
        from AppKit import NSTableView, NSScrollView, NSTableColumn

        self._items = items or []
        self._callback = callback

        # Create the container view
        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, dimensions[0], dimensions[1] + 10))

        # Create scroll view
        self._scroll_view = NSScrollView.alloc().initWithFrame_(NSMakeRect(5, 5, dimensions[0] - 10, dimensions[1]))
        self._scroll_view.setHasVerticalScroller_(True)
        self._scroll_view.setHasHorizontalScroller_(False)
        self._scroll_view.setAutohidesScrollers_(True)
        self._scroll_view.setBorderType_(1)  # NSLineBorder

        # Create a simple list using NSTableView with minimal setup
        # We'll use a simpler approach that doesn't require complex data source protocols
        from AppKit import NSOutlineView, NSBrowserCell
        self._table_view = NSTableView.alloc().init()
        self._table_view.setHeaderView_(None)  # Hide header
        self._table_view.setIntercellSpacing_(NSSize(0, 1))
        self._table_view.setRowHeight_(20)
        self._table_view.setRefusesFirstResponder_(False)

        if allow_multiple_selection:
            self._table_view.setAllowsMultipleSelection_(True)
        else:
            self._table_view.setAllowsMultipleSelection_(False)

        # Create table column
        column = NSTableColumn.alloc().initWithIdentifier_("items")
        column.setWidth_(dimensions[0] - 30)  # Account for scrollbar and padding
        self._table_view.addTableColumn_(column)

        # Use a simpler approach - populate table directly without complex data source
        self._populate_table()

        # Set up scroll view
        self._scroll_view.setDocumentView_(self._table_view)

        # Set up the menu item
        self._menuitem = NSMenuItem.alloc().init()
        self._menuitem.setTarget_(NSApp)
        self._view.addSubview_(self._scroll_view)
        self._menuitem.setView_(self._view)

        # Store callback
        NSApp._ns_to_py_and_callback[self._table_view] = self, callback

    def _populate_table(self):
        """Populate the table with items using a simple approach."""
        # For now, let's use a simpler implementation
        # We'll add items as simple rows without complex data source protocols
        pass

    def __repr__(self):
        return '<{0}: [items: {1}; callback: {2}]>'.format(
            type(self).__name__,
            len(self._items),
            repr(self._callback)
        )

    def set_items(self, items):
        """Set the list of items to display."""
        self._items = items or []
        self._populate_table()

    def get_items(self):
        """Get the current list of items."""
        return self._items

    def get_selected_item(self):
        """Get the currently selected item."""
        selected_row = self._table_view.selectedRow()
        if 0 <= selected_row < len(self._items):
            return self._items[selected_row]
        return None

    def get_selected_index(self):
        """Get the index of the currently selected item."""
        return self._table_view.selectedRow()

    def add_item(self, item):
        """Add an item to the list."""
        self._items.append(item)
        self._populate_table()

    def remove_item(self, index):
        """Remove an item from the list by index."""
        if 0 <= index < len(self._items):
            del self._items[index]
            self._populate_table()

    def clear_items(self):
        """Remove all items from the list."""
        self._items.clear()
        self._populate_table()

    def set_callback(self, callback):
        """Set the function serving as callback for when an item is selected."""
        self._callback = callback
        NSApp._ns_to_py_and_callback[self._table_view] = self, callback

    @property
    def callback(self):
        """Return the current callback function."""
        return self._callback

    @property
    def items(self):
        """The current list of items."""
        return self._items

    @items.setter
    def items(self, new_items):
        self.set_items(new_items)


class CardMenuItem(object):
    """Represents a card-style menu item with leading icon and title text.

    A single fixed-height row that contains a circular icon and title text.
    The card is hoverable and provides visual feedback on interaction.

    :param title: the main text for the card.
    :param leading_icon: path to an icon displayed in a circular colored background.
    :param icon_color: background color for the icon circle (e.g., blue, red).
    :param callback: the function serving as callback for when the card is clicked.
    :param dimensions: a sequence of numbers whose length is two, specifying the dimensions of the card.
    """

    def __init__(self, title="", leading_icon=None, icon_color=None, callback=None, dimensions=(250, 44)):
        from AppKit import NSTextField, NSImageView, NSColor, NSButton, NSFont

        self._title = title
        self._leading_icon = leading_icon
        self._icon_color = icon_color or NSColor.systemBlueColor()
        self._callback = callback
        self._dimensions = dimensions

        width, height = dimensions

        # Create the container view (no background, transparent)
        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))
        self._view.setWantsLayer_(True)

        # Card layout constants
        left_margin = 12
        icon_size = 32
        icon_spacing = 12

        # Leading icon with circular colored background
        current_x = left_margin
        self._icon_container = None
        self._leading_icon_view = None

        if leading_icon:
            # Create circular icon container
            icon_y = (height - icon_size) // 2
            self._icon_container = NSView.alloc().initWithFrame_(
                NSMakeRect(current_x, icon_y, icon_size, icon_size)
            )
            self._icon_container.setWantsLayer_(True)
            self._icon_container.layer().setCornerRadius_(icon_size / 2)  # Perfect circle

            # Set icon background color
            if isinstance(icon_color, tuple) and len(icon_color) >= 3:
                r, g, b = icon_color[:3]
                a = icon_color[3] if len(icon_color) > 3 else 1.0
                color = NSColor.colorWithRed_green_blue_alpha_(r, g, b, a)
            else:
                color = icon_color or NSColor.systemBlueColor()

            self._icon_container.layer().setBackgroundColor_(color.CGColor())

            # Create icon image view (centered in circle)
            icon_padding = 6
            self._leading_icon_view = NSImageView.alloc().initWithFrame_(
                NSMakeRect(icon_padding, icon_padding, icon_size - (icon_padding * 2), icon_size - (icon_padding * 2))
            )
            self._leading_icon_view.setImageScaling_(1)  # NSImageScaleProportionallyUpOrDown
            self._leading_icon_view.setImageFrameStyle_(0)  # NSImageFrameNone

            # Load and set the icon
            self._set_icon_image(self._leading_icon_view, leading_icon, (icon_size - (icon_padding * 2), icon_size - (icon_padding * 2)))

            self._icon_container.addSubview_(self._leading_icon_view)
            self._view.addSubview_(self._icon_container)
            current_x += icon_size + icon_spacing

        # Title text (single line, medium weight)
        text_width = width - current_x - 12  # 12px right margin
        title_y = (height - 20) // 2  # Center vertically

        self._title_field = NSTextField.alloc().initWithFrame_(
            NSMakeRect(current_x, title_y, text_width, 20)
        )
        self._title_field.setStringValue_(title)
        self._title_field.setEditable_(False)
        self._title_field.setSelectable_(False)
        self._title_field.setBordered_(False)
        self._title_field.setDrawsBackground_(False)

        # Title font: medium weight, appropriate size
        title_font = NSFont.systemFontOfSize_weight_(15, AppKit.NSFontWeightMedium)
        self._title_field.setFont_(title_font)
        self._title_field.setTextColor_(NSColor.labelColor())

        # Truncate long text with ellipsis
        self._title_field.cell().setLineBreakMode_(AppKit.NSLineBreakByTruncatingTail)

        self._view.addSubview_(self._title_field)

        # Create invisible button for click and hover handling
        self._button = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))
        self._button.setButtonType_(6)  # NSMomentaryChangeButton
        self._button.setBordered_(False)
        self._button.setTransparent_(True)
        self._button.setTarget_(NSApp)
        self._button.setAction_('cardCallback:')

        # Set up hover tracking
        tracking_area = AppKit.NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
            NSMakeRect(0, 0, width, height),
            AppKit.NSTrackingMouseEnteredAndExited | AppKit.NSTrackingActiveInKeyWindow,
            self,
            None
        )
        self._view.addTrackingArea_(tracking_area)

        self._view.addSubview_(self._button)

        # Set up the menu item
        self._menuitem = NSMenuItem.alloc().init()
        self._menuitem.setTarget_(NSApp)
        self._menuitem.setView_(self._view)

        # Track hover state
        self._is_hovered = False

        self.set_callback(callback)

    def mouseEntered_(self, event):
        """Handle mouse entering the card for hover effect."""
        self._is_hovered = True
        # Create subtle highlight effect (lighter background)
        hover_color = NSColor.controlAccentColor().colorWithAlphaComponent_(0.15)
        self._view.layer().setBackgroundColor_(hover_color.CGColor())

    def mouseExited_(self, event):
        """Handle mouse exiting the card."""
        self._is_hovered = False
        # Return to transparent background
        self._view.layer().setBackgroundColor_(NSColor.clearColor().CGColor())

    def _set_icon_image(self, image_view, icon_path, dimensions):
        """Helper method to set an icon image with proper scaling."""
        if icon_path:
            try:
                image = _nsimage_from_file(icon_path, dimensions=dimensions)
                if image:
                    image_view.setImage_(image)
            except Exception as e:
                _log(f'CardMenuItem: error loading icon from {icon_path}: {e}')

    def __repr__(self):
        return '<{0}: [title: {1}; icon: {2}; callback: {3}]>'.format(
            type(self).__name__,
            repr(self._title),
            repr(self._leading_icon),
            repr(self.callback)
        )

    def set_callback(self, callback):
        """Set the function serving as callback for when the card is clicked.

        :param callback: the function to be called when the user clicks on the card.
        """
        self._callback = callback
        NSApp._ns_to_py_and_callback[self._button] = self, callback

    @property
    def callback(self):
        """Return the current callback function."""
        return NSApp._ns_to_py_and_callback.get(self._button, (None, None))[1]

    @property
    def title(self):
        """The main text of the card."""
        return self._title

    @title.setter
    def title(self, new_title):
        self._title = new_title
        self._title_field.setStringValue_(new_title)

    def set_leading_icon(self, icon_path, icon_color=None):
        """Set the leading icon and optionally its background color.

        :param icon_path: path to the image file, or None to clear the icon.
        :param icon_color: background color for the icon circle.
        """
        self._leading_icon = icon_path
        if self._leading_icon_view and icon_path:
            self._set_icon_image(self._leading_icon_view, icon_path,
                               (self._leading_icon_view.frame().size.width,
                                self._leading_icon_view.frame().size.height))

        # Update icon background color if provided
        if self._icon_container and icon_color:
            if isinstance(icon_color, tuple) and len(icon_color) >= 3:
                r, g, b = icon_color[:3]
                a = icon_color[3] if len(icon_color) > 3 else 1.0
                color = NSColor.colorWithRed_green_blue_alpha_(r, g, b, a)
            else:
                color = icon_color
            self._icon_container.layer().setBackgroundColor_(color.CGColor())


class SeparatorMenuItem(object):
    """Visual separator between :class:`rumps.MenuItem` objects in the application menu."""
    def __init__(self):
        self._menuitem = NSMenuItem.separatorItem()


class Timer(object):
    """
    Python abstraction of an Objective-C event timer in a new thread for application. Controls the callback function,
    interval, and starting/stopping the run loop.

    .. versionchanged:: 0.2.0
       Method `__call__` removed.

    :param callback: Function that should be called every `interval` seconds. It will be passed this
                     :class:`rumps.Timer` object as its only parameter.
    :param interval: The time in seconds to wait before calling the `callback` function.
    """
    def __init__(self, callback, interval):
        self.set_callback(callback)
        self._interval = interval
        self._status = False

    def __repr__(self):
        return ('<{0}: [callback: {1}; interval: {2}; '
                'status: {3}]>').format(type(self).__name__, repr(getattr(self, '*callback').__name__),
                                        self._interval, 'ON' if self._status else 'OFF')

    @property
    def interval(self):
        """The time in seconds to wait before calling the :attr:`callback` function."""
        return self._interval  # self._nstimer.timeInterval() when active but could be inactive

    @interval.setter
    def interval(self, new_interval):
        if self._status:
            if abs(self._nsdate.timeIntervalSinceNow()) >= self._nstimer.timeInterval():
                self.stop()
                self._interval = new_interval
                self.start()
        else:
            self._interval = new_interval

    @property
    def callback(self):
        """The current function specified as the callback."""
        return getattr(self, '*callback')

    def is_alive(self):
        """Whether the timer thread loop is currently running."""
        return self._status

    def start(self):
        """Start the timer thread loop."""
        if not self._status:
            self._nsdate = NSDate.date()
            self._nstimer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
                self._nsdate, self._interval, self, 'callback:', None, True)
            NSRunLoop.currentRunLoop().addTimer_forMode_(self._nstimer, NSDefaultRunLoopMode)
            _TIMERS[self] = None
            self._status = True

    def stop(self):
        """Stop the timer thread loop."""
        if self._status:
            self._nstimer.invalidate()
            del self._nstimer
            del self._nsdate
            self._status = False

    def set_callback(self, callback):
        """Set the function that should be called every :attr:`interval` seconds. It will be passed this
        :class:`rumps.Timer` object as its only parameter.
        """
        setattr(self, '*callback', callback)

    def callback_(self, _):
        _log(self)
        try:
            return _internal.call_as_function_or_method(getattr(self, '*callback'), self)
        except Exception:
            traceback.print_exc()


class Window(object):
    """Generate a window to consume user input in the form of both text and button clicked.

    .. versionchanged:: 0.2.0
        Providing a `cancel` string will set the button text rather than only using text "Cancel". `message` is no
        longer a required parameter.

    .. versionchanged:: 0.3.0
        Add `secure` text input field functionality.

    :param message: the text positioned below the `title` in smaller font. If not a string, will use the string
                    representation of the object.
    :param title: the text positioned at the top of the window in larger font. If not a string, will use the string
                  representation of the object.
    :param default_text: the text within the editable textbox. If not a string, will use the string representation of
                         the object.
    :param ok: the text for the "ok" button. Must be either a string or ``None``. If ``None``, a default
               localized button title will be used.
    :param cancel: the text for the "cancel" button. If a string, the button will have that text. If `cancel`
                   evaluates to ``True``, will create a button with text "Cancel". Otherwise, this button will not be
                   created.
    :param dimensions: the size of the editable textbox. Must be sequence with a length of 2.
    :param secure: should the text field be secured or not. With ``True`` the window can be used for passwords.
    """

    def __init__(self, message='', title='', default_text='', ok=None, cancel=None, dimensions=(320, 160),
                 secure=False):
        message = text_type(message)
        message = message.replace('%', '%%')
        title = text_type(title)

        self._cancel = bool(cancel)
        self._icon = None

        _internal.require_string_or_none(ok)
        if not isinstance(cancel, string_types):
            cancel = 'Cancel' if cancel else None

        self._alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
            title, ok, cancel, None, message)
        self._alert.setAlertStyle_(0)  # informational style

        if secure:
            self._textfield = SecureEditing.alloc().initWithFrame_(NSMakeRect(0, 0, *dimensions))
        else:
            self._textfield = Editing.alloc().initWithFrame_(NSMakeRect(0, 0, *dimensions))
        self._textfield.setSelectable_(True)
        self._alert.setAccessoryView_(self._textfield)

        self.default_text = default_text

    @property
    def title(self):
        """The text positioned at the top of the window in larger font. If not a string, will use the string
        representation of the object.
        """
        return self._alert.messageText()

    @title.setter
    def title(self, new_title):
        new_title = text_type(new_title)
        self._alert.setMessageText_(new_title)

    @property
    def message(self):
        """The text positioned below the :attr:`title` in smaller font. If not a string, will use the string
        representation of the object.
        """
        return self._alert.informativeText()

    @message.setter
    def message(self, new_message):
        new_message = text_type(new_message)
        self._alert.setInformativeText_(new_message)

    @property
    def default_text(self):
        """The text within the editable textbox. An example would be

            "Type your message here."

        If not a string, will use the string representation of the object.
        """
        return self._default_text

    @default_text.setter
    def default_text(self, new_text):
        new_text = text_type(new_text)
        self._default_text = new_text
        self._textfield.setStringValue_(new_text)

    @property
    def icon(self):
        """The path to an image displayed for this window. If set to ``None``, will default to the icon for the
        application using :attr:`rumps.App.icon`.

        .. versionchanged:: 0.2.0
           If the icon is set to an image then changed to ``None``, it will correctly be changed to the application
           icon.

        """
        return self._icon

    @icon.setter
    def icon(self, icon_path):
        new_icon = _nsimage_from_file(icon_path) if icon_path is not None else None
        self._icon = icon_path
        self._alert.setIcon_(new_icon)

    def add_button(self, name):
        """Create a new button.

        .. versionchanged:: 0.2.0
           The `name` parameter is required to be a string.

        :param name: the text for a new button. Must be a string.
        """
        _internal.require_string(name)
        self._alert.addButtonWithTitle_(name)

    def add_buttons(self, iterable=None, *args):
        """Create multiple new buttons.

        .. versionchanged:: 0.2.0
           Since each element is passed to :meth:`rumps.Window.add_button`, they must be strings.

        """
        if iterable is None:
            return
        if isinstance(iterable, string_types):
            self.add_button(iterable)
        else:
            for ele in iterable:
                self.add_button(ele)
        for arg in args:
            self.add_button(arg)

    def run(self):
        """Launch the window. :class:`rumps.Window` instances can be reused to retrieve user input as many times as
        needed.

        :return: a :class:`rumps.rumps.Response` object that contains the text and the button clicked as an integer.
        """
        _log(self)
        if NSUserDefaults.standardUserDefaults().stringForKey_('AppleInterfaceStyle') == 'Dark':
            self._alert.window().setAppearance_(AppKit.NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark'))
        clicked = self._alert.runModal() % 999
        if clicked > 2 and self._cancel:
            clicked -= 1
        self._textfield.validateEditing()
        text = self._textfield.stringValue()
        self.default_text = self._default_text  # reset default text
        return Response(clicked, text)


class Response(object):
    """Holds information from user interaction with a :class:`rumps.Window` after it has been closed."""

    def __init__(self, clicked, text):
        self._clicked = clicked
        self._text = text

    def __repr__(self):
        shortened_text = self._text if len(self._text) < 21 else self._text[:17] + '...'
        return '<{0}: [clicked: {1}, text: {2}]>'.format(type(self).__name__, self._clicked, repr(shortened_text))

    @property
    def clicked(self):
        """Return a number representing the button pressed by the user.

        The "ok" button will return ``1`` and the "cancel" button will return ``0``. This makes it convenient to write
        a conditional like,

        .. code-block:: python

            if response.clicked:
                do_thing_for_ok_pressed()
            else:
                do_thing_for_cancel_pressed()

        Where `response` is an instance of :class:`rumps.rumps.Response`.

        Additional buttons added using methods :meth:`rumps.Window.add_button` and :meth:`rumps.Window.add_buttons`
        will return ``2``, ``3``, ... in the order they were added.
        """
        return self._clicked

    @property
    def text(self):
        """Return the text collected from the user."""
        return self._text


class NSApp(NSObject):
    """Objective-C delegate class for NSApplication. Don't instantiate - use App instead."""

    _ns_to_py_and_callback = {}

    def userNotificationCenter_didActivateNotification_(self, notification_center, notification):
        notifications._clicked(notification_center, notification)

    def initializeStatusBar(self):
        self.nsstatusitem = NSStatusBar.systemStatusBar().statusItemWithLength_(-1)  # variable dimensions
        self.nsstatusitem.setHighlightMode_(True)

        self.setStatusBarIcon()
        self.setStatusBarTitle()

        mainmenu = self._app['_menu']
        quit_button = self._app['_quit_button']
        if quit_button is not None:
            quit_button.set_callback(quit_application)
            mainmenu.add(quit_button)
        else:
            _log('WARNING: the default quit button is disabled. To exit the application gracefully, another button '
                 'should have a callback of quit_application or call it indirectly.')
        self.nsstatusitem.setMenu_(mainmenu._menu)  # mainmenu of our status bar spot (_menu attribute is NSMenu)

    def showMenu(self):
        self.nsstatusitem.button().performClick_(None)

    def setStatusBarTitle(self):
        self.nsstatusitem.setTitle_(self._app['_title'])
        self.fallbackOnName()

    def setStatusBarIcon(self):
        self.nsstatusitem.setImage_(self._app['_icon_nsimage'])
        self.fallbackOnName()

    def fallbackOnName(self):
        if not (self.nsstatusitem.title() or self.nsstatusitem.image()):
            self.nsstatusitem.setTitle_(self._app['_name'])

    def applicationDidFinishLaunching_(self, notification):
        workspace          = NSWorkspace.sharedWorkspace()
        notificationCenter = workspace.notificationCenter()
        notificationCenter.addObserver_selector_name_object_(
            self,
            self.receiveSleepNotification_,
            NSWorkspaceWillSleepNotification,
            None
        )
        notificationCenter.addObserver_selector_name_object_(
            self,
            self.receiveWakeNotification_,
            NSWorkspaceDidWakeNotification,
            None
        )

    def receiveSleepNotification_(self, ns_notification):
        _log('receiveSleepNotification')
        events.on_sleep.emit()

    def receiveWakeNotification_(self, ns_notification):
        _log('receiveWakeNotification')
        events.on_wake.emit()

    def applicationWillTerminate_(self, ns_notification):
        _log('applicationWillTerminate')
        events.before_quit.emit()

    @classmethod
    def callback_(cls, nsmenuitem):
        self, callback = cls._ns_to_py_and_callback[nsmenuitem]
        _log(self)
        try:
            return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()

    @classmethod
    def textFieldCallback_(cls, nstextfield):
        """Callback for TextFieldMenuItem when text changes or Enter is pressed."""
        self, callback = cls._ns_to_py_and_callback[nstextfield]
        _log(self)
        try:
            return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()

    @classmethod
    def imageCallback_(cls, nsimageview):
        """Callback for ImageMenuItem when image is clicked."""
        self, callback = cls._ns_to_py_and_callback[nsimageview]
        _log(self)
        try:
            return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()

    @classmethod
    def listSelectionCallback_(cls, nscombobox_or_notification):
        """Callback for ListMenuItem when NSComboBox selection changes."""
        try:
            # Handle both direct NSComboBox objects and NSNotification objects
            if hasattr(nscombobox_or_notification, 'object') and nscombobox_or_notification.object():
                # This is an NSNotification, get the combo box from it
                nscombobox = nscombobox_or_notification.object()
            else:
                # This is a direct NSComboBox object
                nscombobox = nscombobox_or_notification

            self, callback = cls._ns_to_py_and_callback[nscombobox]
            _log(self)

            # Update internal tracking
            self._selected_index = nscombobox.indexOfSelectedItem()

            # Call user callback
            if callback:
                return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()

    @classmethod
    def cardCallback_(cls, nsbutton):
        """Callback for CardMenuItem when card is clicked."""
        self, callback = cls._ns_to_py_and_callback[nsbutton]
        _log(self)
        try:
            if callback:
                return _internal.call_as_function_or_method(callback, self)
        except Exception:
            traceback.print_exc()


class App(object):
    """Represents the statusbar application.

    Provides a simple and pythonic interface for all those long and ugly `PyObjC` calls. :class:`rumps.App` may be
    subclassed so that the application logic can be encapsulated within a class. Alternatively, an `App` can be
    instantiated and the various callback functions can exist at module level.

    .. versionchanged:: 0.2.0
       `name` parameter must be a string and `title` must be either a string or ``None``. `quit_button` parameter added.

    :param name: the name of the application.
    :param title: text that will be displayed for the application in the statusbar.
    :param icon: file path to the icon that will be displayed for the application in the statusbar.
    :param menu: an iterable of Python objects or pairs of objects that will be converted into the main menu for the
                 application. Parsing is implemented by calling :meth:`rumps.MenuItem.update`.
    :param quit_button: the quit application menu item within the main menu. If ``None``, the default quit button will
                        not be added.
    """

    # NOTE:
    # Serves as a setup class for NSApp since Objective-C classes shouldn't be instantiated normally.
    # This is the most user-friendly way.

    #: A serializer for notification data.  The default is pickle.
    serializer = pickle

    def __init__(self, name, title=None, icon=None, template=None, menu=None, quit_button='Quit'):
        _internal.require_string(name)
        self._name = name
        self._icon = self._icon_nsimage = self._title = None
        self._template = template
        self.icon = icon
        self.title = title
        self.quit_button = quit_button
        self._menu = Menu()
        if menu is not None:
            self.menu = menu
        self._application_support = application_support(self._name)

    # Properties
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @property
    def name(self):
        """The name of the application. Determines the application support folder name. Will also serve as the title
        text of the application if :attr:`title` is not set.
        """
        return self._name

    @property
    def title(self):
        """The text that will be displayed for the application in the statusbar. Can be ``None`` in which case the icon
        will be used or, if there is no icon set the application text will fallback on the application :attr:`name`.

        .. versionchanged:: 0.2.0
           If the title is set then changed to ``None``, it will correctly be removed. Must be either a string or
           ``None``.

        """
        return self._title

    @title.setter
    def title(self, title):
        _internal.require_string_or_none(title)
        self._title = title
        try:
            self._nsapp.setStatusBarTitle()
        except AttributeError:
            pass

    @property
    def icon(self):
        """A path to an image representing the icon that will be displayed for the application in the statusbar.
        Can be ``None`` in which case the text from :attr:`title` will be used.

        .. versionchanged:: 0.2.0
           If the icon is set to an image then changed to ``None``, it will correctly be removed.

        """
        return self._icon

    @icon.setter
    def icon(self, icon_path):
        new_icon = _nsimage_from_file(icon_path, template=self._template) if icon_path is not None else None
        self._icon = icon_path
        self._icon_nsimage = new_icon
        try:
            self._nsapp.setStatusBarIcon()
        except AttributeError:
            pass

    @property
    def template(self):
        """Template mode for an icon. If set to ``None``, the current icon (if any) is displayed as a color icon.
        If set to ``True``, template mode is enabled and the icon will be displayed correctly in dark menu bar mode.
        """
        return self._template

    @template.setter
    def template(self, template_mode):
        self._template = template_mode
        # resetting the icon to apply template setting
        self.icon = self._icon

    @property
    def menu(self):
        """Represents the main menu of the statusbar application. Setting `menu` works by calling
        :meth:`rumps.MenuItem.update`.
        """
        return self._menu

    @menu.setter
    def menu(self, iterable):
        self._menu.update(iterable)

    @property
    def quit_button(self):
        """The quit application menu item within the main menu. This is a special :class:`rumps.MenuItem` object that
        will both replace any function callback with :func:`rumps.quit_application` and add itself to the end of the
        main menu when :meth:`rumps.App.run` is called. If set to ``None``, the default quit button will not be added.

        .. warning::
           If set to ``None``, some other menu item should call :func:`rumps.quit_application` so that the
           application can exit gracefully.

        .. versionadded:: 0.2.0

        """
        return self._quit_button

    @quit_button.setter
    def quit_button(self, quit_text):
        if quit_text is None:
            self._quit_button = None
        else:
            self._quit_button = MenuItem(quit_text)

    # Show status item
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def showMenu(self):
        self._nsapp.showMenu()

    # Open files in application support folder
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def open(self, *args):
        """Open a file within the application support folder for this application.

        .. code-block:: python

            app = App('Cool App')
            with app.open('data.json') as f:
                pass

        Is a shortcut for,

        .. code-block:: python

            app = App('Cool App')
            filename = os.path.join(application_support(app.name), 'data.json')
            with open(filename) as f:
                pass

        """
        return open(os.path.join(self._application_support, args[0]), *args[1:])

    # Run the application
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def run(self, **options):
        """Performs various setup tasks including creating the underlying Objective-C application, starting the timers,
        and registering callback functions for click events. Then starts the application run loop.

        .. versionchanged:: 0.2.1
            Accepts `debug` keyword argument.

        :param debug: determines if application should log information useful for debugging. Same effect as calling
                      :func:`rumps.debug_mode`.

        """
        dont_change = object()
        debug = options.get('debug', dont_change)
        if debug is not dont_change:
            debug_mode(debug)

        nsapplication = NSApplication.sharedApplication()
        nsapplication.activateIgnoringOtherApps_(True)  # NSAlerts in front
        self._nsapp = NSApp.alloc().init()
        self._nsapp._app = self.__dict__  # allow for dynamic modification based on this App instance
        nsapplication.setDelegate_(self._nsapp)
        notifications._init_nsapp(self._nsapp)

        setattr(App, '*app_instance', self)  # class level ref to running instance (for passing self to App subclasses)
        t = b = None
        for t in getattr(timer, '*timers', []):
            t.start()
        for b in getattr(clicked, '*buttons', []):
            b(self)  # we waited on registering clicks so we could pass self to access _menu attribute
        del t, b

        self._nsapp.initializeStatusBar()

        AppHelper.installMachInterrupt()
        events.before_start.emit()
        AppHelper.runEventLoop()

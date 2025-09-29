# -*- coding: utf-8 -*-
"""
app.py — App class for rumps-style macOS status bar apps.
"""

import os
import pickle

from AppKit import NSApplication
from Foundation import NSSearchPathForDirectoriesInDomains
from PyObjCTools import AppHelper

# Internal helpers / signals
from ..utils import internal as _internal
from ..utils.helpers import debug_mode, nsimage_from_file as _nsimage_from_file
from ..notifications import _init_nsapp
from ..events import before_start
from .nsapp import NSApp

# These are required types used by App (menu container + items).
# They may live in another module in your refactor; we try a couple of common locations.
from ..menu_items import Menu, MenuItem  # preferred if you've split menu classes out


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

        # Compute application support dir here (inline, to avoid depending on a helper function location)
        app_support_root = NSSearchPathForDirectoriesInDomains(14, 1, 1).objectAtIndex_(0)
        self._application_support = os.path.join(app_support_root, self._name)
        if not os.path.isdir(self._application_support):
            os.mkdir(self._application_support)

    # Properties
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

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

    # Convenience
    def showMenu(self):
        self._nsapp.showMenu()

    # File access in Application Support
    def open(self, *args):
        """Open a file within the application support folder for this application."""
        return open(os.path.join(self._application_support, args[0]), *args[1:])

    # Run the application
    def run(self, **options):
        """Create the ObjC application, start timers, register click callbacks, and start the run loop.

        .. versionchanged:: 0.2.1
            Accepts `debug` keyword argument.
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
        _init_nsapp(self._nsapp)

        # Start any @timer decorated callbacks collected elsewhere
        # and register any @clicked/... decorators. We import lazily to keep this
        # module containing only the App class.
        setattr(App, '*app_instance', self)  # class level ref to running instance (for passing self to App subclasses)
        t = b = None
        for t in getattr(timer, '*timers', []):
            t.start()
        for b in getattr(clicked, '*buttons', []):
            b(self)  # we waited on registering clicks so we could pass self to access _menu attribute
        del t, b

        self._nsapp.initializeStatusBar()

        AppHelper.installMachInterrupt()
        before_start.emit()
        AppHelper.runEventLoop()

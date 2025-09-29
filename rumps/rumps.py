#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""
Main rumps module - imports from refactored structure.
Package entry point, from here we must be able to use every class or methods defined in the package
"""

import Foundation
import AppKit
import objc
from objc import super, signature

from Foundation import (NSDate, NSTimer, NSRunLoop, NSDefaultRunLoopMode, NSSearchPathForDirectoriesInDomains,
                        NSUserDomainMask, NSApplicationSupportDirectory, NSMutableDictionary, NSMutableArray,
                        NSObject, NSString, NSMakeRect, NSUserDefaults)
from AppKit import NSApplication, NSStatusBar, NSMenu, NSMenuItem, NSAlert, NSTextField, NSSecureTextField, NSImage, NSSlider, NSSize, NSWorkspace, NSWorkspaceWillSleepNotification, NSWorkspaceDidWakeNotification, NSView
from PyObjCTools import AppHelper

import os
import pickle
import traceback
import weakref

# Import from refactored structure
from .utils.compat import text_type, string_types, iteritems, collections_abc
from .utils.listdict import ListDict
from .utils import internal as _internal
from .utils.helpers import debug_mode, _log, nsimage_from_file as _nsimage_from_file

from .menu_items import (
    Menu,
    MenuItem,
    SeparatorMenuItem,
    separator,
    SliderMenuItem,
    TextFieldMenuItem,
    ImageMenuItem,
    ListMenuItem,
    ListView,
    CardMenuItem
)

from .events import (
    EventEmitter,
    before_start,
    on_notification as event_on_notification,
    on_sleep,
    on_wake,
    before_quit
)
from . import events

from .notifications import (
    Notification,
    on_notification,
    notify as notification,
    _init_nsapp,
    _clicked
)

from .core import (
    Timer,
    Window,
    Response,
    NSApp,
    App
)

from .decorators import (
    timer,
    clicked,
    slider,
    textfield,
    image,
    list_menu,
    card
)


# Initialize debug mode
debug_mode(True)

# Global variables
separator = object()  # Sentinel object for separators
_TIMERS = weakref.WeakKeyDictionary()

# ========================================================================
# Functions that haven't been refactored yet
# ========================================================================

def alert(title=None, message='', ok=None, cancel=None, other=None, icon_path=None):
    """Generate a simple alert window."""
    _internal.require_string_or_none(ok)
    if cancel is not None and not isinstance(cancel, bool):
        _internal.require_string(cancel)
    _log('alert opened with message: {0}, title: {1}'.format(repr(message), repr(title)))
    alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(
        title, ok, cancel, other, message)
    if icon_path is not None:
        icon = _nsimage_from_file(icon_path)
        alert.setIcon_(icon)
    _log('alert received: {0}'.format(alert.runModal()))
    return alert.runModal()


def application_support(name):
    """Return the application support folder path for the given app name."""
    app_support_path = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, True)[0]
    app_support_path = os.path.join(app_support_path, name)
    if not os.path.isdir(app_support_path):
        os.mkdir(app_support_path)
    return app_support_path


def timers():
    """Return a list of all active Timer objects."""
    return list(_TIMERS.keys())


def quit_application(sender=None):
    """Quit the application."""
    _log('closing application')
    NSApplication.sharedApplication().terminate_(sender)




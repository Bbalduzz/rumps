#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""
rumps
=====

Ridiculously Uncomplicated macOS Python Statusbar apps.

rumps exposes Objective-C classes as Python classes and functions which greatly simplifies the process of creating a
statusbar application.
"""

# Version info
from .__version__ import __title__, __version__, __author__, __license__, __copyright__

# Import from refactored structure while maintaining backward compatibility
try:
    # Try to import from new structure
    from .menu_items import (
        SliderMenuItem,
        TextFieldMenuItem, ImageMenuItem, ListMenuItem,
        ListView, CardMenuItem, separator
    )
    # During transition, use the original MenuItem and SeparatorMenuItem to avoid conflicts
    from .rumps import MenuItem, SeparatorMenuItem

    # Import utilities
    from .utils.helpers import debug_mode

    # For now, import remaining items from original rumps.py
    # These will be gradually migrated to the new structure
    from .rumps import (
        alert, application_support, timers, quit_application,
        timer, clicked, Timer, Window, Response, NSApp, App,
        slider, textfield, image, list_menu, card,
        EventEmitter, events, Notification
    )
except ImportError:
    # Fallback to original structure if new structure is not complete
    from .rumps import (
        separator, debug_mode, alert, application_support, timers, quit_application,
        timer, clicked, MenuItem, SliderMenuItem, TextFieldMenuItem, ImageMenuItem,
        ListMenuItem, ListView, CardMenuItem, SeparatorMenuItem, Timer, Window, Response, NSApp, App,
        slider, textfield, image, list_menu, card,
        EventEmitter, events, Notification
    )

# Notifications
from . import notifications as _notifications
notifications = _notifications.on_notification
notification = _notifications.notify

# Public API
__all__ = [
    # Core classes
    'App', 'Timer', 'Window', 'Response', 'NSApp',
    # Menu items
    'MenuItem', 'SeparatorMenuItem', 'SliderMenuItem',
    'TextFieldMenuItem', 'ImageMenuItem', 'ListMenuItem',
    'ListView', 'CardMenuItem', 'separator',
    # Event system
    'EventEmitter', 'events',
    # Decorators
    'clicked', 'timer', 'slider', 'textfield',
    'image', 'list_menu', 'card',
    # Functions
    'debug_mode', 'alert', 'application_support',
    'quit_application', 'timers',
    # Notifications
    'Notification', 'notification', 'notifications',
    # Version info
    '__title__', '__version__', '__author__', '__license__', '__copyright__'
]

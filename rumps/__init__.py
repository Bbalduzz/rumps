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

__title__ = 'rumps'
__version__ = '0.4.0-5'
__author__ = 'Jared Suttles'
__license__ = 'Modified BSD'
__copyright__ = 'Copyright 2020 Jared Suttles'

from . import notifications as _notifications
from .rumps import (separator, debug_mode, alert, application_support, timers, quit_application, timer,
                    clicked, MenuItem, SliderMenuItem, TextFieldMenuItem, ImageMenuItem, ListMenuItem, ListView,
                    CardMenuItem, Timer, Window, App, slider, textfield, image, list_menu, card)

notifications = _notifications.on_notification
notification = _notifications.notify

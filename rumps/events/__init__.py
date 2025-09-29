#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Event system for rumps."""

from .emitter import EventEmitter

# Pre-defined event emitters for common application events
before_start = EventEmitter('before_start')
on_notification = EventEmitter('on_notification')
on_sleep = EventEmitter('on_sleep')
on_wake = EventEmitter('on_wake')
before_quit = EventEmitter('before_quit')

__all__ = [
    'EventEmitter',
    'before_start',
    'on_notification',
    'on_sleep',
    'on_wake',
    'before_quit'
]
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Notification system for rumps."""

from .notification import Notification
from .center import (
    on_notification,
    notify,
    _init_nsapp,
    _clicked
)

__all__ = [
    'Notification',
    'on_notification',
    'notify',
    '_init_nsapp',
    '_clicked'
]
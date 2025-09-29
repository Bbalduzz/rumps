#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Notification class for rumps."""

import datetime
from ..utils.compat import text_type, collections_abc


class Notification(collections_abc.Mapping):
    """Represents a macOS notification with its data and properties."""

    def __init__(self, ns_user_notification, data):
        self._ns = ns_user_notification
        self._data = data

    def __repr__(self):
        return '<{0}: [data: {1}]>'.format(type(self).__name__, repr(self._data))

    @property
    def title(self):
        """The notification title."""
        return text_type(self._ns.title())

    @property
    def subtitle(self):
        """The notification subtitle."""
        return text_type(self._ns.subtitle())

    @property
    def message(self):
        """The notification message."""
        return text_type(self._ns.informativeText())

    @property
    def activation_type(self):
        """How the notification was activated."""
        activation_type = self._ns.activationType()
        if activation_type == 1:
            return 'contents_clicked'
        elif activation_type == 2:
            return 'action_button_clicked'
        elif activation_type == 3:
            return 'replied'
        elif activation_type == 4:
            return 'additional_action_clicked'

    @property
    def delivered_at(self):
        """When the notification was delivered."""
        ns_date = self._ns.actualDeliveryDate()
        seconds = ns_date.timeIntervalSince1970()
        dt = datetime.datetime.fromtimestamp(seconds)
        return dt

    @property
    def response(self):
        """User's response to the notification (if any)."""
        ns_attributed_string = self._ns.response()
        if ns_attributed_string is None:
            return None
        ns_string = ns_attributed_string.string()
        return text_type(ns_string)

    @property
    def data(self):
        """Custom data associated with the notification."""
        return self._data

    def _check_if_mapping(self):
        if not isinstance(self._data, collections_abc.Mapping):
            raise TypeError(
                'notification cannot be used as a mapping when data is not a '
                'mapping'
            )

    def __getitem__(self, key):
        self._check_if_mapping()
        return self._data[key]

    def __iter__(self):
        self._check_if_mapping()
        return iter(self._data)

    def __len__(self):
        self._check_if_mapping()
        return len(self._data)
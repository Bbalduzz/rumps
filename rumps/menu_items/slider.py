#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""SliderMenuItem class for rumps."""

from AppKit import NSView, NSSlider, NSMenuItem, NSApp, NSMakeRect, NSSize

from .base import BaseMenuItem


class SliderMenuItem(BaseMenuItem):
    """
    Represents a slider menu item within the application's menu.

    :param value: a number for the current position of the slider.
    :param min_value: a number for the minimum position to which a slider can be moved.
    :param max_value: a number for the maximum position to which a slider can be moved.
    :param callback: the function serving as callback for when a slide event occurs on this menu item.
    :param dimensions: a sequence of numbers whose length is two, specifying the dimensions of the slider.
    """

    def __init__(self, value=50, min_value=0, max_value=100, callback=None, dimensions=(180, 15)):
        super(SliderMenuItem, self).__init__()
        self._view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 0, 30))
        self._slider = NSSlider.alloc().init()
        self._slider.setMinValue_(min_value)
        self._slider.setMaxValue_(max_value)
        self._slider.setDoubleValue_(int(value))
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
        """Return the current callback function."""
        if hasattr(NSApp, '_ns_to_py_and_callback'):
            return NSApp._ns_to_py_and_callback.get(self._slider, (None, None))[1]
        return None

    @property
    def value(self):
        """The current position of the slider."""
        return self._slider.doubleValue()

    @value.setter
    def value(self, new_value):
        self._slider.setDoubleValue_(int(new_value))
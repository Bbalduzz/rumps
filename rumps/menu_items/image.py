#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""ImageMenuItem class for rumps."""

from AppKit import (
    NSView, NSImageView, NSMenuItem, NSApp, NSMakeRect,
    NSImage, NSColor, NSButton
)

from .base import BaseMenuItem
from ..utils.helpers import nsimage_from_file, _log


class ImageMenuItem(BaseMenuItem):
    """
    Represents an image display menu item within the application's menu.

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
        super(ImageMenuItem, self).__init__()

        # Determine dimensions - use image size if not specified
        if dimensions is None and image_path:
            # Load image to get its natural dimensions WITHOUT forcing size
            try:
                # Load image without setting size to get natural dimensions
                temp_image = NSImage.alloc().initByReferencingFile_(image_path)
                if temp_image:
                    image_size = temp_image.size()
                    view_width, view_height = int(image_size.width), int(image_size.height)
                    _log('ImageMenuItem: using natural image size {0}x{1}'.format(view_width, view_height))
                else:
                    # Fallback if image can't be loaded
                    view_width, view_height = 150, 100
                    _log('ImageMenuItem: failed to load image, using fallback size')
            except Exception as e:
                # Fallback if image can't be loaded
                view_width, view_height = 150, 100
                _log('ImageMenuItem: error loading image {0}, using fallback size'.format(e))
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
        """
        Set the image to display.

        :param image_path: path to the image file, or None to clear the image.
        """
        if image_path is None:
            self._image_view.setImage_(None)
            self._image_path = None
            return

        try:
            # Use nsimage_from_file with the view dimensions to properly scale
            image = nsimage_from_file(image_path, dimensions=self._dimensions)
            if image:
                self._image_view.setImage_(image)
                self._image_path = image_path
                _log('ImageMenuItem: loaded image from {0}'.format(image_path))
            else:
                _log('ImageMenuItem: failed to load image from {0}'.format(image_path))
        except Exception as e:
            _log('ImageMenuItem: error loading image from {0}: {1}'.format(image_path, e))

    def set_callback(self, callback):
        """
        Set the function serving as callback for when the image is clicked.

        :param callback: the function to be called when the user clicks on the image.
        """
        # During transition, handle NSApp not being initialized yet
        try:
            if hasattr(NSApp, '_ns_to_py_and_callback'):
                if hasattr(self, '_button'):
                    NSApp._ns_to_py_and_callback[self._button] = self, callback
                else:
                    NSApp._ns_to_py_and_callback[self._image_view] = self, callback
        except AttributeError:
            # NSApp not properly initialized yet, skip for now
            pass

    @property
    def callback(self):
        """Return the current callback function."""
        if hasattr(NSApp, '_ns_to_py_and_callback'):
            if hasattr(self, '_button'):
                return NSApp._ns_to_py_and_callback.get(self._button, (None, None))[1]
            else:
                return NSApp._ns_to_py_and_callback.get(self._image_view, (None, None))[1]
        return None

    @property
    def image_path(self):
        """The path to the currently displayed image."""
        return self._image_path

    @property
    def dimensions(self):
        """The current dimensions of the image view."""
        return self._dimensions
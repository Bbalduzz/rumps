#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""TextFieldMenuItem class for rumps."""

from Foundation import NSString
from AppKit import NSView, NSMenuItem, NSApp, NSMakeRect

from .base import BaseMenuItem
# During transition, import text field classes that are already defined
# This avoids Objective-C class duplication errors
try:
    # Try to import from the already-loaded module to avoid re-registration
    import rumps.utils.text_field as tf
    Editing = tf.Editing
    SecureEditing = tf.SecureEditing
except (ImportError, AttributeError):
    # Fallback if not already loaded
    from AppKit import NSTextField, NSSecureTextField
    Editing = NSTextField
    SecureEditing = NSSecureTextField


class TextFieldMenuItem(BaseMenuItem):
    """
    Represents a text input field menu item within the application's menu.

    A text field that can be embedded directly in the menu, allowing inline text input
    without the need for modal dialogs.

    :param text: the initial text value for the text field.
    :param placeholder: placeholder text shown when the field is empty.
    :param callback: the function serving as callback for when text changes or Enter is pressed.
    :param dimensions: a sequence of numbers whose length is two, specifying the dimensions of the text field.
    :param secure: whether to use a secure text field (for passwords).
    """

    def __init__(self, text="", placeholder="", callback=None, dimensions=(180, 20), secure=False):
        super(TextFieldMenuItem, self).__init__()

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
        """
        Set the function serving as callback for when text changes or Enter is pressed.

        :param callback: the function to be called when the user types or presses Enter.
        """
        # During transition, handle NSApp not being initialized yet
        try:
            if hasattr(NSApp, '_ns_to_py_and_callback'):
                NSApp._ns_to_py_and_callback[self._textfield] = self, callback
        except AttributeError:
            # NSApp not properly initialized yet, skip for now
            pass
        self._textfield.setAction_('textFieldCallback:' if callback is not None else None)

    @property
    def callback(self):
        """Return the current callback function."""
        if hasattr(NSApp, '_ns_to_py_and_callback'):
            return NSApp._ns_to_py_and_callback.get(self._textfield, (None, None))[1]
        return None

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
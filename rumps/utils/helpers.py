#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rumps: Ridiculously Uncomplicated macOS Python Statusbar apps.
# Copyright: (c) 2020, Jared Suttles. All rights reserved.
# License: BSD, see LICENSE for details.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

"""Helper functions for rumps."""

import os
from Foundation import NSLog
from AppKit import NSImage

_log = lambda *_: None


def debug_mode(choice):
    """Enable/disable printing helpful information for debugging the program. Default is off."""
    global _log
    if choice:
        def log_func(*args):
            NSLog(' '.join(map(str, args)))
        _log = log_func
    else:
        _log = lambda *_: None


__all__ = ['debug_mode', 'nsimage_from_file', '_log']

def nsimage_from_file(filename, dimensions=None, template=None):
    """Take a path to an image file and return an NSImage object."""
    try:
        _log('attempting to open image at {0}'.format(filename))
        with open(filename):
            pass
    except IOError:
        try:
            from __main__ import __file__ as main_script_path
            main_script_path = os.path.dirname(main_script_path)
            filename = os.path.join(main_script_path, filename)
        except ImportError:
            pass
        _log('attempting (again) to open image at {0}'.format(filename))
        with open(filename):
            pass
    image = NSImage.alloc().initByReferencingFile_(filename)
    image.setScalesWhenResized_(True)
    image.setSize_((20, 20) if dimensions is None else dimensions)
    if template is not None:
        image.setTemplate_(template)
    return image